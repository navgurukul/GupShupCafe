"""
Base Dict Model
Provides dict-like functionality to Pydantic models
"""

from pydantic import BaseModel
from typing import Any, Iterator, Dict


class DictMixin:
    """Mixin class that adds dict-like functionality to Pydantic models"""
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: model['field_name']"""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' not found in {self.__class__.__name__}")
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-style assignment: model['field_name'] = value"""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"'{key}' not found in {self.__class__.__name__}")
    
    def __delitem__(self, key: str) -> None:
        """Allow dict-style deletion: del model['field_name']"""
        if hasattr(self, key):
            delattr(self, key)
        else:
            raise KeyError(f"'{key}' not found in {self.__class__.__name__}")
    
    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator: 'field_name' in model"""
        return hasattr(self, key)
    
    def __iter__(self) -> Iterator[str]:
        """Allow iteration over field names: for field in model"""
        return iter(self.model_fields.keys())
    
    def __len__(self) -> int:
        """Return number of fields: len(model)"""
        return len(self.model_fields)
    
    def keys(self):
        """Return field names like dict.keys()"""
        return self.model_fields.keys()
    
    def values(self):
        """Return field values like dict.values()"""
        return [getattr(self, key) for key in self.model_fields.keys()]
    
    def items(self):
        """Return field name-value pairs like dict.items()"""
        return [(key, getattr(self, key)) for key in self.model_fields.keys()]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get field value with default like dict.get()"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def pop(self, key: str, default: Any = None) -> Any:
        """Remove and return field value like dict.pop()"""
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            if default is not None:
                return default
            raise
    
    def update(self, other: Dict[str, Any]) -> None:
        """Update multiple fields like dict.update()"""
        for key, value in other.items():
            if key in self:
                self[key] = value
            else:
                raise KeyError(f"'{key}' not found in {self.__class__.__name__}")
    
    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set field to default if not exists, return current value like dict.setdefault()"""
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default
    
    def clear(self) -> None:
        """Clear all fields (set to None/default values)"""
        for key in self.model_fields.keys():
            field_info = self.model_fields[key]
            if field_info.default is not None:
                self[key] = field_info.default
            elif field_info.default_factory is not None:
                self[key] = field_info.default_factory()
            else:
                self[key] = None
    
    def copy(self):
        """Return a copy of the model like dict.copy()"""
        return self.model_copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to regular Python dict"""
        return self.model_dump()
    
    def from_dict(self, data: Dict[str, Any]):
        """Create new instance from dict"""
        return self.__class__(**data)


class BaseDictModel(BaseModel, DictMixin):
    """Base model class that combines Pydantic BaseModel with dict-like functionality"""
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        arbitrary_types_allowed = True
        
    def __repr__(self) -> str:
        """Enhanced repr showing dict-like nature"""
        fields = ", ".join(f"{k}={repr(v)}" for k, v in self.items())
        return f"{self.__class__.__name__}({fields})"