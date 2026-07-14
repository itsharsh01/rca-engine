from core.taxonomy import FaultClass

class FaultInjector:
    def inject_fault(self, app_id: str, fault: FaultClass) -> bool:
        """
        Break target application app_id in 6 known ways for testing.
        """
        return True

    def restore_app(self, app_id: str) -> bool:
        """
        Restore original state and undo injected faults.
        """
        return True
