import os
from datetime import datetime

import requests as r
from flask import Flask, request, render_template, redirect, url_for, flash

from data_models import db, Author, Book

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'platinum-dragon'

db.init_app(app)


@app.route('/')
def home():
    authors = Author.query.all()
    books = Book.query.all()

    search_term = request.args.get('search_query', '').strip()

    sort_by = request.args.get('sort_by')

    if search_term:
        books = [book for book in books if search_term.lower() in book.title.lower() or (
                book.author and search_term.lower() in book.author.name.lower())]

    enriched_books = [book for book in books if book.author]

    if sort_by == 'publication_date':
        enriched_books.sort(key=lambda book: book.publication_date or datetime.min.date())
    elif sort_by == 'author':
        enriched_books.sort(key=lambda book: book.author.name)
    else:

        enriched_books.sort(key=lambda book: book.title)

    return render_template('homepage.html', authors=authors, books=enriched_books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['author_name']
        birth_date_str = request.form['birth_date']
        date_of_death_str = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        date_of_death = None

        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date()

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(new_author)
        db.session.commit()

        return "Author added successfully!"
    else:
        authors = Author.query.all()
        return render_template('add_author.html', authors=authors)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        publication_date_str = request.form.get('publication_date')
        author_id_str = request.form['author_id']

        publication_date = None
        if publication_date_str:
            publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
        author_id = int(author_id_str)
        author = Author.query.get(author_id)
        cover_url = None

        if author:
            google_books_url = 'https://www.googleapis.com/books/v1/volumes'
            params = {
                'q': f"{title} {author.name}"
            }
            try:
                response = r.get(google_books_url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                if data.get('items'):
                    item = data['items'][0]
                    if 'imageLinks' in item['volumeInfo']:
                        cover_url = item['volumeInfo']['imageLinks'].get('thumbnail')
                        print(f"Google Books: Found cover for '{title}'")
            except r.exceptions.RequestException as e:
                print(f"Google Books API Error: {e}")

        new_book = Book(title=title, publication_date=publication_date,
                        author_id=author_id, cover_url=cover_url)

        db.session.add(new_book)
        db.session.commit()

        return "Book successfully added!"
    else:
        authors = Author.query.all()
        return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    author = book_to_delete.author
    delete_author_too = (len(author.books) == 1)

    db.session.delete(book_to_delete)
    db.session.commit()

    if delete_author_too:
        db.session.delete(author)
        db.session.commit()

    flash('Book deleted successfully!')
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author_to_delete = Author.query.get_or_404(author_id)

    for book in author_to_delete.books:
        db.session.delete(book)

    db.session.delete(author_to_delete)
    db.session.commit()

    flash('Author and all of their books deleted successfully!')
    return redirect(url_for('home'))


if __name__ == '__main__':
    # ↓↓↓ UNCOMMENT BELOW TO CREATE/UPDATE DB ↓↓↓
    # with app.app_context():
    #  db.create_all()
    app.run(debug=True)
