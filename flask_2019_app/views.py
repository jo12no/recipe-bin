from flask import render_template, flash, redirect, url_for, request
from flask_2019_app import app, db
from flask_2019_app.forms import login_form, registration_form, publish_form, search_form, edit_form
# flask login
from flask_login import current_user, login_user, login_required, logout_user
from flask_2019_app.models import user, posts, tag
# image upload 
from google.cloud import storage
# url encode the post title
from urllib.parse import quote_plus

@app.route('/index')
@app.route('/')
@login_required
def index():
	# get page number from query string
	page = request.args.get('page', 1, type=int)
	posts_to_show = posts.query.paginate(page, app.config['POSTS_PER_PAGE'], True)

	# page urls
	if posts_to_show.has_next:
		next_page_url = url_for('index', page=posts_to_show.next_num)
	else:
		next_page_url = None

	if posts_to_show.has_prev:
		prev_page_url = url_for('index', page=posts_to_show.prev_num)
	else:
		prev_page_url = None

	index = True # to get the current page URL for navbar highlighting

	return render_template('index.html', posts=posts_to_show.items, # .items for pagination
							next_page_url=next_page_url, prev_page_url=prev_page_url, index=index) 

@app.route('/post/<id>')
def post(id):
	encoded_id = quote_plus(id) # the id was decoded, so encode it 
	post_to_show = posts.query.filter_by(title_urlify=encoded_id).first_or_404()
	return render_template('post.html', post=post_to_show)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated: # from flask_login
		return redirect(url_for('index'))

	form = login_form()
	# POST
	if form.validate_on_submit(): 
		user_to_login = user.query.filter_by(username=form.username.data).first()
		if user_to_login is None or not user_to_login.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user_to_login, remember=form.remember_me.data) # all good so log the user in 
		return redirect(url_for('index'))

	return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated: # from flask_login
		return redirect(url_for('index'))

	form = registration_form()
	# POST
	if form.validate_on_submit(): 
		user_to_commit = user(username=form.username.data, email=form.email.data)
		user_to_commit.set_password(form.password.data)
		db.session.add(user_to_commit)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))

	return render_template('register.html', form=form)

@app.route('/publish',  methods=['GET', 'POST'])
@login_required
def publish():
	form = publish_form()
	publish = True # to get the current page URL for navbar highlighting
	# POST
	if form.validate_on_submit():
		""" Image upload from form """
		uploaded_file = request.files.get('image')
		if uploaded_file.filename == '':
			uploaded_file_url = "https://storage.googleapis.com/{}/default.jpg".format(app.config['CLOUD_STORAGE_BUCKET'])
			print(uploaded_file_url)
		else:
			uploaded_file = request.files.get('image')
			# Create a Cloud Storage client.
			gcs = storage.Client.from_service_account_json(app.config['GOOGLE_APPLICATION_CREDENTIALS'])

			# Get the bucket that the file will be uploaded to.
			bucket = gcs.get_bucket(app.config['CLOUD_STORAGE_BUCKET'])

			# Create a new blob and upload the file's content.
			blob = bucket.blob(uploaded_file.filename)

			blob.upload_from_string(
				uploaded_file.read(),
				content_type=uploaded_file.content_type
			)

			uploaded_file_url = blob.public_url

		""" tags """ 
		new_tags_to_add = []
		existing_tags_to_append = []
		tags = ''.join(form.tags.data).split(',') # comma seperate 	
		for x in tags:
			if tag.query.filter_by(name=x).count() == 0:
				tag(name=x) # the tag doesn't yet exist, so create it and add to the post
				new_tags_to_add.append(tag(name=x))
			else: # we'll append the existing tag to the post object later
				existing_tags_to_append.append(tag.query.filter(tag.name==x).first())

		post_to_commit = posts(
							title=form.title.data,
							title_urlify=quote_plus(form.title.data[0:50].lower().replace(' ', '-')),
							body=form.body.data,
							ingredients=form.ingredients.data,
							image_url=uploaded_file_url,
							tags = new_tags_to_add,
							user_id=current_user.id) # current_user from flask login
		db.session.add(post_to_commit)

		# append existing tags to post object
		for x in existing_tags_to_append:
			x.posts.append(post_to_commit)

		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))

	return render_template('publish.html', form=form, publish=publish)

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
	encoded_id = quote_plus(id) # the id was decoded, so encode it 
	post_to_show = posts.query.filter_by(title_urlify=encoded_id).first_or_404()
	form = edit_form()
	# POST
	if form.validate_on_submit():
		""" Image upload from form """
		uploaded_file = request.files.get('image')
		if uploaded_file.filename == '':
			uploaded_file_url = post_to_show.image_url
		else:
			# Create a Cloud Storage client.
			gcs = storage.Client.from_service_account_json(app.config['GOOGLE_APPLICATION_CREDENTIALS'])

			# Get the bucket that the file will be uploaded to.
			bucket = gcs.get_bucket(app.config['CLOUD_STORAGE_BUCKET'])

			# Create a new blob and upload the file's content.
			blob = bucket.blob(uploaded_file.filename)

			blob.upload_from_string(
				uploaded_file.read(),
				content_type=uploaded_file.content_type
			)

			uploaded_file_url = blob.public_url

		""" tags """ 
		new_tags_to_add = []
		existing_tags_to_append = []
		tags = ''.join(form.tags.data).split(',') # comma seperate 	
		for x in tags:
			if tag.query.filter_by(name=x).count() == 0:
				tag(name=x) # the tag doesn't yet exist, so create it and add to the post
				new_tags_to_add.append(tag(name=x))
			else: # we'll append the existing tag to the post object later
				new_tags_to_add.append(tag.query.filter(tag.name==x).first())

		post_to_show.title=form.title.data
		post_to_show.title_urlify=quote_plus(form.title.data[0:50].lower().replace(' ', '-'))
		post_to_show.body=form.body.data
		post_to_show.ingredients=form.ingredients.data
		post_to_show.image_url=uploaded_file_url
		post_to_show.tags = new_tags_to_add

		db.session.commit()

		flash('Your edits were saved!')
		return redirect(url_for('index'))

	elif request.method == 'GET':
		# populate tags field from existing post
		tags_for_html = []
		count = 0
		for x in post_to_show.tags:
			if count == 0:
				tags_for_html.append(post_to_show.tags[count].name.strip())
			elif count == 1:
				tags_for_html.append(',' + post_to_show.tags[count].name.strip() + ',')
			else:
				tags_for_html.append(post_to_show.tags[count].name.strip() + ',')
			count += 1

		formatted_tags = ''.join(tags_for_html)
		# prepopulate form fields
		form.title.data = post_to_show.title
		form.body.data = post_to_show.body
		form.ingredients.data = post_to_show.ingredients
		form.tags.data = formatted_tags.rstrip(',')

	return render_template('edit.html', form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
	form = search_form()
	query_from_url = request.args.get('q', type=str)

	# POST
	if form.validate_on_submit():
		return redirect(url_for('search', q=form.search_term.data))

	# There is no search term in the URL, so return the form
	if query_from_url is None:
		return render_template('search.html', form=form)
	
	# We've got a search term, so let's process it
	joined_query_from_url = query_from_url.split(' ')

	search_results_array = []
	for x in joined_query_from_url:
		search_var = '%' + x + '%' 
		search_query = search_results_array.append(posts.query.join(posts.tags).filter((posts.title.like(search_var) |
									posts.body.like(search_var) |
									posts.ingredients.like(search_var) |
									tag.name.like(search_var)
									)).all())

	unpacked_search_results_array = sum(search_results_array, []) # since the array nests results from each search keyword

	if len(unpacked_search_results_array) < 1: 
		flash('No search results found!')
	return render_template('search.html', form=form, posts=unpacked_search_results_array)

@app.route('/delete/<id>')
@login_required
def delete(id):
	encoded_id = quote_plus(id) # the id was decoded, so encode it 
	post_to_delete = posts.query.filter_by(title_urlify=encoded_id).first_or_404()

	db.session.delete(post_to_delete)
	db.session.commit()

	flash('Post deleted!')
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))