from app import db

class data_log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    source = db.Column(db.String(64),index=True)
    datatype = db.Column(db.String(64),index=True)
    time = db.Column(db.DateTime,index=True)
    payload = db.Column(db.String(2048))

    def __repr__(self):
        return '<entry: '+self.datatype + ' from ' + \
               self.source + ' at ' +self.time.strftime("%H %M %S")+' >'

class machines(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256),index=True)
    ident = db.Column(db.String(256),index=True)
    
    def __repr__(self):
        return '< Machine: '+self.name+' >'

class cell_info(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    shifts=db.Column(db.PickleType())
    takt=db.Column(db.Integer)

    def __repr__(self):
        return '< Cell: '+self.name+' >'
