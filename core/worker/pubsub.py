import json
import asyncio
import datetime
from typing import Dict, Any, List
from google.cloud import pubsub_v1
from core.config import settings
from core.database import get_database

# Determine if we should fallback to a simulated local queue (mock)
use_mock_queue = not all([settings.gcp_project_id, settings.gcp_topic_id, settings.gcp_subscription_id])

class PubSubManager:
    def __init__(self):
        self.project_id = settings.gcp_project_id
        self.topic_id = settings.gcp_topic_id
        self.subscription_id = settings.gcp_subscription_id
        
        if not use_mock_queue:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
                self.subscriber = pubsub_v1.SubscriberClient()
                self.subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)
                self.mock = False
            except Exception as e:
                print(f"Warning: Failed to initialize Google Pub/Sub clients, falling back to mock queue. Error: {e}")
                self.mock = True
        else:
            self.mock = True
            print("Using mock queue for trace extraction tasks (GCP Pub/Sub config is incomplete).")

    def publish_task(self, payload: Dict[str, Any]) -> None:
        message_data = json.dumps(payload).encode("utf-8")
        if not self.mock:
            try:
                future = self.publisher.publish(self.topic_path, message_data)
                print(f"Published message ID to GCP Pub/Sub: {future.result()}")
            except Exception as e:
                print(f"GCP Pub/Sub publish warning: {e}")

        # Always trigger trace extraction execution worker to guarantee MongoDB trace persistence
        asyncio.create_task(self._process_mock_message(payload))

    async def _process_mock_message(self, payload: Dict[str, Any]) -> None:
        # Simulate quick network delay and run callback
        await asyncio.sleep(0.1)
        await execute_trace_extraction_task(payload)

    def start_subscriber(self, loop) -> Any:
        if self.mock:
            print("[MOCK QUEUE] Subscriber started (polling local queue)...")
            return None
        
        def callback(message):
            try:
                data = json.loads(message.data.decode("utf-8"))
                print(f"GCP Pub/Sub received task message: {data}")
                
                fut = asyncio.run_coroutine_threadsafe(
                    execute_trace_extraction_task(data), 
                    loop
                )
                
                def done_cb(f):
                    try:
                        f.result()
                        message.ack()
                        print(f"Successfully processed and acked GCP Pub/Sub message for {data.get('diagnosis_id')}")
                    except Exception as exc:
                        print(f"Task execution failed: {exc}")
                        message.nack()
                
                fut.add_done_callback(done_cb)
            except Exception as e:
                print(f"Failed to process GCP Pub/Sub message: {e}")
                message.nack()

        # concurrency configuration: limit to 5 messages concurrently in flow control
        flow_control = pubsub_v1.types.FlowControl(max_messages=5)
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, 
            callback=callback,
            flow_control=flow_control
        )
        print(f"GCP Pub/Sub listening on subscription {self.subscription_path} with 5 concurrent message slots...")
        return streaming_pull_future

async def execute_trace_extraction_task(payload: Dict[str, Any]) -> None:
    app_id = payload.get("app_id")
    platform = payload.get("platform_name")
    diagnosis_id = payload.get("diagnosis_id")
    start_time = payload.get("start_time")
    end_time = payload.get("end_time")
    
    print(f"Extracting traces for App: {app_id}, Platform: {platform}, Diagnosis ID: {diagnosis_id} from {start_time} to {end_time}")
    
    # 1. Fetch credentials from MongoDB configurations collection (fallback if missing)
    db = get_database()
    config_doc = await db.configurations.find_one({"platform_name": platform.lower()})
    credentials = config_doc.get("credentials", {}) if config_doc else {}
    
    # 2. Invoke appropriate adapter
    from adapters.langsmith_adapter import LangsmithAdapter
    from adapters.langfuse_adapter import LangfuseAdapter
    from adapters.otel_jaeger_adapter import OtelJaegerAdapter
    from adapters.helicone_adapter import HeliconeAdapter
    from adapters.phoenix_adapter import PhoenixAdapter
    
    adapter = None
    if platform == "langsmith":
        adapter = LangsmithAdapter()
    elif platform == "langfuse":
        adapter = LangfuseAdapter()
    elif platform == "phoenix":
        adapter = PhoenixAdapter()
    elif platform == "helicone":
        adapter = HeliconeAdapter()
    elif platform in ("otel", "jaeger"):
        adapter = OtelJaegerAdapter()
        
    if not adapter:
        print(f"Error: Unknown adapter platform {platform}")
        return
        
    # 3. Fetch data
    try:
        raw_traces = await adapter.fetch_traces(start_time=start_time, end_time=end_time)
        print(f"Fetched {len(raw_traces)} raw traces from {platform}.")
        
        # 4. Ingest traces to DB
        from core.ingestion import IngestPipeline
        pipeline = IngestPipeline()
        for trace in raw_traces:
            await pipeline.ingest(trace, diagnosis_id=diagnosis_id)
        print(f"Successfully ingested {len(raw_traces)} traces into MongoDB for diagnosis {diagnosis_id}.")
    except Exception as e:
        print(f"Failed to fetch or ingest traces from {platform}: {e}")
