#! coding: utf8

import web
import datetime
from models import sqlaSession


class SQLAStore(web.session.Store):
    def __init__(self, table):  # , tableIn):
        self.table = table
        # self.tableIn = tableIn
        self.session = sqlaSession

    def __contains__(self, key):
        # return bool(
        #     sql_session.execute(
        #         self.table.select(self.table.c.session_id==key)
        #     ).fetchone()
        # )
        return bool(
            self.session.query(self.table).filter_by(session_id=key).all()
        )

    def __getitem__(self, key):
        q = self.session.query(self.table).filter_by(session_id=key).first()
        if q is None:
            raise KeyError
        else:
            # sql_session.execute(self.table.update().values(atime=datetime.datetime.now()).where(self.table.c.session_id==key))
            q.atime = datetime.datetime.now()
            self.session.add(q)
            self.session.commit()
            return self.decode(q.data)

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        if key in self:
            q = self.session.query(self.table).filter_by(session_id=key).first()
            q.data = pickled
        else:
            q = self.table(session_id=key, data=pickled)

        self.session.add(q)
        self.session.commit()

    def __delitem__(self, key):
        q = self.session.query(self.table).filter_by(session_id=key).first()
        if q:
            self.session.delete(q)
            self.session.commit()

    def cleanup(self, timeout):
        timeout = datetime.timedelta(timeout/(24.0*60*60))
        last_allowed_time = datetime.datetime.now() - timeout
        q = self.session.query(self.table).filter(
            self.table.atime < last_allowed_time
        ).all()
        for eachQ in q:
            self.session.delete(eachQ)

        self.session.commit()
