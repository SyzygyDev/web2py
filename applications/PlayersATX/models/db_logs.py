# coding: utf8

db.define_table('staff_logs',
                Field('staff_id', 'reference auth_user'),
				Field('staff_action', 'string', writable=True),
				Field('created', 'datetime', writable=False, default=request.now))