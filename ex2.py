# 自分自身とrelationのあるテーブルを定義する

import json
import os
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, declarative_base

# db2.sqliteを削除
DB_FILE = "./db2.sqlite"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)


engine = create_engine(f"sqlite:///{DB_FILE}",
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("items.id"))

    # 自分自身とのrelationの場合、remote_sideを指定する
    parent = relationship("Item", back_populates="children", remote_side=id)
    children = relationship("Item", back_populates="parent")


Base.metadata.create_all(bind=engine)
db = SessionLocal()

seed_json = """
[
  {
    "id": 1,
    "content": "This is a test comment",
    "parent_id": null
  },
  {
    "id": 2,
    "content": "This is another test comment",
    "parent_id": 1
  }
]
"""

seed = json.loads(seed_json)
for item in seed:
    db.add(Item(**item))

db.commit()

item = db.query(Item).filter(Item.id == 1).first()
print("Item", item.id, item.content, item.parent, item.children)
