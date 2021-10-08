from teacher_dasboard.database import SessionLocal

class DatabaseSession:
    def __init__(self):
        print("creating db session")
        self.db = SessionLocal()

    def get(self):
        try:
            yield self.db
        except Exception as e:
            self.db.rollback()
            raise e
    
    def __del__(self):
        print("closing db session")
        self.db.close()
