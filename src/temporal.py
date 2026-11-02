class TemporalConfirm:
    """Scene-level confirmation for one monitored zone; not per-pet tracking."""
    def __init__(self, frames_required=5, clear_frames=5):
        self.frames_required=frames_required
        self.clear_frames=clear_frames
        self.streak=0
        self.misses=0
        self.active=False

    def update(self, violating):
        new_event=False
        if violating:
            self.streak+=1
            self.misses=0
            if not self.active and self.streak>=self.frames_required:
                self.active=True
                new_event=True
        else:
            self.streak=0
            self.misses+=1
            if self.misses>=self.clear_frames:
                self.active=False
        return self.active,new_event
