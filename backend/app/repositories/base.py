from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """根据主键查询"""
        return self.db.query(self.model).get(id)

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[ModelType], int]:
        """分页查询"""
        query = self.db.query(self.model)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_all(self) -> List[ModelType]:
        """查询全部"""
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> ModelType:
        """创建单条记录"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_batch(self, objs_in: List[dict]) -> List[ModelType]:
        """批量创建"""
        db_objs = [self.model(**obj) for obj in objs_in]
        self.db.add_all(db_objs)
        self.db.commit()
        for obj in db_objs:
            self.db.refresh(obj)
        return db_objs

    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """更新记录"""
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """删除记录"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
