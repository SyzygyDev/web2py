# coding: utf8

db.define_table('player_data',
				Field('user_id', 'reference auth_user'),
				Field('gender', requires=IS_IN_SET(["Male", "Female"]), writable=True),
				Field('date_of_birth', 'date', writable=True),
				Field('address', 'string', writable=True),
				Field('city', 'string', writable=True),
				Field('state', 'string', writable=True),
				Field('zip_code', 'string', writable=True),
				Field('phone', 'string', writable=True),
				Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('teams',
				Field('team_name', 'string', writable=True),
				Field('created_by', 'integer'),
				Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('team_members',
				Field('team_id', 'reference teams'),
				Field('player_id', 'integer'),
				Field('added', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('player_registry',
				Field('tourn_id', 'reference tournament'),
				Field('player_id', 'integer'),
				Field('registered', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('tourn_teams',
				Field('tourn_id', 'reference tournament'),
				Field('team_id', 'integer'),
				Field('added', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('tourn_games',
				Field('tourn_id', 'reference tournament'),
				Field('bracket_place', 'string', writable=True),
				Field('team_a', 'integer'),
				Field('team_b', 'integer'),
				Field('team_a_score', 'integer'),
				Field('team_b_score', 'integer'),
				Field('updated', 'datetime', writable=False, default=request.now, update=request.now))