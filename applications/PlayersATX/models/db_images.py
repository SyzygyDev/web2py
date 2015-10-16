# coding: utf8

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