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

db.define_table('locations',
				Field('name', 'string', writable=True, label='Location Name'),
				Field('google_place_id', 'string', writable=False),
				Field('location_address', 'string', writable=True, label='Location address'),
				Field('location_url', 'string', writable=True, label='Location web site'),
				Field('location_img', 'integer', writable=True, label='Location image from uploads'),
				Field('location_img_url', 'string', writable=True, label='Location image from url', comment="please include 'http://' or 'https://'"))

db.define_table('tournament_types',
				Field('tourn_type', 'string', writable=False))

db.define_table('tournament',
				Field('name', 'string', writable=True, label='Tournament Name'),
				Field('tourn_date', 'datetime', writable=True, label='Tournament Date'),
				Field('register_date', 'datetime', writable=True, default=request.now, label='Registration Date', comment="Online registration starts on this day, leave it blank to allow immedeate registration"),
				Field('location_id', 'integer', requires=IS_IN_DB(db, db.locations.id, '%(name)s', zero=None), writable=True, label='Location?'),
				Field('description', 'text', writable=True, label='Tournament Description'),
				Field('tourn_type', 'integer', requires=IS_IN_DB(db, db.tournament_types.id, '%(tourn_type)s', zero=None), default=1, writable=True, label='Tournament type?'),
				Field('tourn_img', 'integer', writable=True, label='Tournament Image'),
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
bannerbox = (450, 260)
site_media.thumbnail.compute = lambda row: image_generator(row.image_file, box, name="thumb")
site_media.banner.compute = lambda row: image_generator(row.image_file, bannerbox, name="banner")

db.define_table('image_key_words',
				Field('image_id', 'reference image_library'),
				Field('key_word', 'string'))