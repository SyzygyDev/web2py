# coding: utf8

db.define_table('content_card',
		Field('card_name', 'string', writable=True, label='Content Card Name'),
		Field('card_heading', 'string', writable=True, label='Content Card Heading'),
		Field('left_image', 'integer', writable=False, label='Left Image'),
		Field('right_image', 'integer', writable=False, label='Right Image'),
		Field('body_text', 'text', writable=True, label='Content'),
		Field('created', 'datetime', writable=False, default=request.now),
		Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('events',
		Field('event_name', 'string', writable=True, label='Event Name'),
		Field('event_heading', 'string', writable=True, label='Event Heading'),
		Field('event_image', 'integer', writable=False, label='Event Image'),
		Field('body_text', 'text', writable=True, label='Content'),
		Field('expiration', 'date', writable=True, label='Event Date', comment="Leave blank for recurring events"),
		Field('prepay', 'boolean', writable=True, default=False, label='Allow on-line payment for this event'),
		Field('created', 'datetime', writable=False, default=request.now),
		Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('partners',
		Field('page_id', 'reference page_settings'),
		Field('partner_name', 'string', writable=True, label='Partner Name'),
		Field('partner_heading', 'string', writable=True, label='Partner Heading'),
		Field('partner_image_link', 'string', writable=True, label='Partner Image URL', comment="if the partners image is just a URL, paste in the link"),
		Field('partner_image', 'integer', writable=True, label='Partner Image', comment="if the partners image is in your image library"),
		Field('display_style', writable=True, requires=IS_IN_SET(['tile', 'banner', 'text only']), default='tile', label='How should this link appear'),
		Field('created', 'datetime', writable=False, default=request.now),
		Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('event_price_label',
		Field('price_label', 'string', writable=True, label='Price Label'))

db.define_table('event_price',
		Field('create_date', 'datetime', writable=False, default=request.now),
		Field('update_date', 'datetime', writable=False, default=request.now, update=request.now),
		Field('event_id', 'reference events'),
		Field('price_label_id', 'reference event_price_label'),
		Field('in_use', 'boolean', writable=True, default=True),
		Field('price', 'decimal(6,2)', writable=True, label='Price Label'))

db.define_table('event_price_group',
                Field('event_price_id', 'reference event_price'),
                Field('event_id', 'reference events'),
                primarykey=['event_price_id','event_id'])

db.define_table('gender_types',
		Field('gender_label', 'string', writable=True, label='Price Label'))

db.define_table('membership_type',
	       Field('membership_label', 'string', writable=True, label='Price Label'))

db.define_table('members',
                Field('member_number', 'string', writable=True),
                Field('auth_table_id', 'reference auth_user'),
                Field('gender', 'reference gender_types'),
                Field('status', 'reference membership_type'),
                Field('his_f_name', 'string', writable=True),
                Field('his_l_name', 'string', writable=True),
                Field('his_email', 'string', writable=True),
                Field('his_dob', 'date', writable=True),
                Field('his_dl', 'string', writable=True),
                Field('her_f_name', 'string', writable=True),
                Field('her_l_name', 'string', writable=True),
                Field('her_email', 'string', writable=True),
                Field('her_dob', 'date', writable=True),
                Field('her_dl', 'string', writable=True),
                Field('address', 'string', writable=True),
                Field('city', 'string', writable=True),
                Field('state', 'string', writable=True),
                Field('zip', 'string', writable=True),
                Field('phone', 'string', writable=True),
                Field('expiration', 'date', writable=True),
                Field('is_pending', 'boolean', writable=True, default=True),
		Field('create_date', 'datetime', writable=False, default=request.now),
		Field('update_date', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('membership_duplicates',
                Field('old_id', 'string', writable=True),
                Field('new_id', 'string', writable=True),
                Field('member_id', 'reference members'),
                Field('fixed', 'boolean', writable=True, default=False))

db.define_table('member_credits',
                Field('member_id', 'reference members'),
                Field('credit', 'string', writable=True),
                Field('created', 'datetime', writable=False, default=request.now),
                Field('used', 'datetime', writable=True))


db.define_table('member_comments',
                Field('member_id', 'reference members'),
                Field('staff_id', 'reference auth_user'),
                Field('create_date', 'datetime', writable=False, default=request.now),
                Field('comment', 'text', writable=True))

db.define_table('purchases',
                Field('purchase_id', 'string', writable=True),
                Field('price_id', 'reference event_price'),
                Field('member_id', 'reference members'),
                Field('f_name', 'string', writable=True),
                Field('l_name', 'string', writable=True),
                Field('e_mail', 'string', writable=True),
                Field('temp_number', 'string', writable=True),
                Field('notes', 'text', writable=True),
                Field('is_pending', 'boolean', writable=True, default=True),
                Field('create_date', 'datetime', writable=False, default=request.now),
		Field('update_date', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('attendance',
                Field('member_id', 'reference members'),
                Field('gender', 'reference gender_types'),
                Field('staff_id', 'reference auth_user'),
                Field('upgrade', 'boolean', writable=True, default=False),
                Field('attend_date', 'date', writable=True),
                Field('credit', 'reference member_credits'),
                Field('created', 'datetime', writable=False, default=request.now))