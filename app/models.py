from app import db

class data_log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    source = db.Column(db.String(64),index=True)
    datatype = db.Column(db.String(64),index=True)
    time = db.Column(db.DateTime,index=True)
    payload = db.Column(db.String(2048))

    def __repr__(self):
        return self.datatype + ' from ' + self.source + ' at ' +self.time.strftime("%H %M %S")
