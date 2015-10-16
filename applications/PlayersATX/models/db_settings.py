# coding: utf8

db.define_table('basic_site',
				Field('page_title', 'string', writable=True, label='Page Title', comment="The title in the browser tab"),
				Field('page_header', 'string', writable=True, label='Page Heading', comment="The main heading at the top of the page"),
				Field('page_footer', 'string', writable=True, label='Page Footer', comment="The banner at the bottom of the page"),
				Field('page_subheader', 'string', writable=True, label='Page Sub Heading', comment="The second heading on the page"),
				Field('page_tagline', 'string', writable=True, label='Page Tag Line', comment="The page tag line under sub heading"),
				Field('page_desc', 'text', writable=True, label='Page Description', comment="The page description used for search engines"),
				Field('background_color', 'string', writable=True, label='Background Color', comment="Hashtag plus 3 or 6 digits, EG #fff or #ffffff"),
				Field('background_img', 'integer', writable=True, label='Page Background Image'),
				Field('background_img_style', writable=True, requires=IS_IN_SET(['tile', 'center', 'stretch']), default='center', label='Background Image Style'),
				Field('modified', 'datetime', writable=False, default=request.now, update=request.now))

db.define_table('page_types',
				Field('page_name', 'string', writable=True, label='Page Name'),
				Field('page_file', 'string', writable=True, label='Page File'),
				Field('is_group', 'boolean', writable=True, default=False, label='Is this a group name'),
				Field('group', 'integer', writable=True, default=0, label='What groups is this a part of'),
				Field('display', 'boolean', writable=True, default=True, label='Display in menu'))

db.define_table('layout_styles',
				Field('layout_label', 'string', writable=False, label='Page Name'))

db.define_table('page_settings',
				Field('page_type', 'reference page_types'),
				Field('data_type', writable=True, requires=IS_IN_SET(['content', 'event', 'partner']), label='Just Content or an Event?'),
				Field('data_card', 'integer', writable=False),
				Field('data_order', 'integer', writable=False),
				Field('alt_image', 'boolean', writable=True, default=False, label='Crop image to fit banner?'),
				Field('layout_style', 'integer', requires=IS_IN_DB(db, db.layout_styles.id, '%(layout_label)s', zero=None), default=1, writable=True, label='Choose a layout style'),
				Field('image_size', 'integer', writable=True, default=25, label='Image Size', comment="how big will the images be (in percentage, but just give us the number)"))