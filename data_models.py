from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", backref='author', lazy=True)

    def __repr__(self):
        return (f"A - {self.name}| ID - {self.id}| "
                f"B - {self.birth_date}| D - {self.date_of_death}")

    def __str__(self):
        if self.date_of_death is not None:
            return f"{self.name} - (ID: {self.id}) {self.birth_date} - {self.date_of_death}"
        else:
            return f"{self.name} - (ID: {self.id}) {self.birth_date}"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    publication_date = db.Column(db.Date, nullable=True)
    cover_url = db.Column(db.String, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __repr__(self):
        return (f"T - {self.title}| ID - {self.id}| "
                f"PD - {self.publication_date}| AId - {self.author_id}")

    def __str__(self):
        return f"{self.title} - (ID: {self.id}) by {self.author.name} (ID: {self.author_id})"
