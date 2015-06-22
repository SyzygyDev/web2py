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
				Field('group', 'integer', writable=True, default=0, label='What groups is this a part of'))

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

site_media = db.define_table('image_library',
				Field('image_name', 'string', writable=True, label='Image Name'),
				Field('image_desc', 'text', writable=True, label='Image Description'),
				Field('keywords', 'string', writable=True, label='Key Words', comment="Words to rapidly search for an image in this system"),
				Field('created', 'datetime', writable=False, default=request.now),
				Field('modified', 'datetime', writable=False, default=request.now, update=request.now),
				Field('image_file', 'upload', requires=IS_IMAGE(extensions=('jpeg', 'png')), autodelete=True, label='Image', comment="Jpegs and PNGs only please"),
				Field('thumbnail', 'upload', autodelete=True),
				Field('banner', 'upload', autodelete=True))

from Media import image_generator
box = (200, 200)
bannerbox = (900, 520)
site_media.thumbnail.compute = lambda row: image_generator(row.image_file, box, name="thumb")
site_media.banner.compute = lambda row: image_generator(row.image_file, bannerbox, name="banner")

db.define_table('image_key_words',
				Field('image_id', 'reference image_library'),
				Field('key_word', 'string'))

db.define_table('script_library',
				Field('script_name', 'string', writable=True, label='Script Name'),
				Field('script_desc', 'text', writable=True, label='Script Description'),
				Field('script_version', 'string', writable=True, label='Script Version'),
				Field('created', 'datetime', writable=False, default=request.now),
				Field('script_file', 'upload', autodelete=True))

db.define_table('style_library',
				Field('style_name', 'string', writable=True, label='Style Sheet Name'),
				Field('style_desc', 'text', writable=True, label='Style Sheet Description'),
				Field('style_version', 'string', writable=True, label='Style Sheet Version'),
				Field('created', 'datetime', writable=False, default=request.now),
				Field('style_file', 'upload', autodelete=True))