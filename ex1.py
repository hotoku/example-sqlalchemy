import os
import click
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import relationship, declarative_base

# db.sqliteを削除
if os.path.exists("./db1.sqlite"):
    os.remove("./db1.sqlite")


@click.group()
def main():
    pass


@click.group()
def db():
    pass


@db.command()
def seed():
    pass


db.add_command(seed)

# RDBMSの違いを吸収するオブジェクト
# `{"check_same_thread": False}`は、SQLite用の設定。
# cf: https://docs.python.org/3/library/sqlite3.html
# マルチスレッドで、同一のコネクションを使う場合にはFalse。
engine = create_engine("sqlite:///./db1.sqlite",
                       connect_args={"check_same_thread": False})


# dbとのセッションを作るオブジェクト
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# モデルクラスのベースとなるクラス
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    items = relationship("Item", back_populates="owner",
                         cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    # Userクラスのitemsという属性と関連付けられる
    # Usersクラスにitemsという属性がないとエラーになる
    owner = relationship("User", back_populates="items")


def create_user(db: Session, name: str):
    db_user = User(name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_item(db: Session, content: str, owner_id: int):
    db_item = Item(content=content, owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ユーザーを作成
user = create_user(db, name="test_user")
print("User", user.id, user.name, user.items)

# itemを作成
item = create_item(db, content="test_item", owner_id=user.id)
print("Item", item.id, item.content, item.owner_id)

# 関連オブジェクトに自動でアイテムが入っている
print("User", user.id, user.name, len(user.items))

# db.query(User).delete([user])
# これ↑は、以下のエラー
# sqlalchemy.exc.ArgumentError: Valid strategies for session synchronization are 'auto', 'evaluate', 'fetch', False


db2 = sessionmaker(bind=engine)()
user2 = db2.query(User).filter(User.id == user.id).first()
db2.delete(user2)  # この場合、user2に関連付けられたitemも削除される
db2.commit()


if __name__ == "__main__":
    main.add_command(db, "db")
