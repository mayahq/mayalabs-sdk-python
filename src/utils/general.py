from pydantic import BaseModel
from typing import List, Optional, Dict

class StepContainer(BaseModel):
    """
    A container for the step object. 
    """
    id : Optional[str]
    type : Optional[str]
    indent_lvl : Optional[int]
    from_node : Optional[str]
    lvl_idx : Optional[int] = 0
    prefix  : Optional[str] = ""
    parent_id : Optional[str] = ""
    error : Optional[str] = None
    children : Optional[List['StepContainer']] = []
    x_coord : Optional[int] = 0
    y_coord : Optional[int] = 0
    scrambled : Optional[bool] = False
    generated : Optional[bool] = False
    generation_id : Optional[str] = ""
    transformed : Optional[bool] = False
    deployed : Optional[bool] = False
    missing_reqs : Optional[List[dict]] = []
    use_cache : Optional[bool] = True

    def has_forks(self):
        assert_has_forks = False
        for child in self.children:
            if child.type == 'fork':
                assert_has_forks = True
        return assert_has_forks
    
    def dict(self):
        return {
            "id" : self.id,
            "step_obj" : self.step_obj.dict() if self.step_obj else None,
            "type" : self.type if self.type else "",
            "indent_lvl" : self.indent_lvl if self.indent_lvl else 0,
            "lvl_idx" : self.lvl_idx if self.lvl_idx else 0,
            "from_node" : self.from_node if self.from_node else "",
            "prefix" : self.prefix if self.prefix else "",
            "parent_id" : self.parent_id if self.parent_id else "",
            "generated" : self.generated,
            "scrambled" : self.scrambled,
            "transformed" : self.transformed,
            "generation_id" : self.generation_id,
            "error" : self.error,
            "deployed" : self.deployed,
            "children" : [child.dict() for child in self.children],
            "use_cache" : self.use_cache,
        }
    def parse_obj(self, json_raw):
        def create_step(step_raw):
            if not isinstance(step_raw, str):
                step = StepContainer()
                step.parse_obj(step_raw)
                return step


        data = json_raw
        if isinstance(data, dict):
            # print("IS DICT",data)
            self.id : str = data["id"]
            self.type : str = data["type"] if "type" in data.keys() else "linear"
            self.indent_lvl : int = data["indent_lvl"] if "indent_lvl" in data.keys() else 0
            self.lvl_idx : int = data["lvl_idx"] if "lvl_idx" in data.keys() else 0
            self.from_node : str = data["from_node"] if "node" in data.keys() else ""
            self.prefix  : str = data["prefix"] if "prefix" in data.keys() else ""
            self.parent_id : str = data["parent_id"] if "parent_id" in data.keys() else ""
            self.children : List['StepContainer'] = [create_step(child) for child in data["children"] if create_step(child)] if "children" in data.keys() else []
            self.generated : bool = data["generated"] if "generated" in data.keys() else False
            self.scrambled : bool = data["scrambled"] if "scrambled" in data.keys() else False
            self.transformed : bool = data["transformed"] if "transformed" in data.keys() else False
            self.error : bool = data["error"] if "error" in data.keys() else None
            self.deployed : bool = data["deployed"] if "deployed" in data.keys() else False
            self.generation_id : str = data["generation_id"] if "generation_id" in data.keys() else ""
            self.use_cache : bool = data["use_cache"] if "use_cache" in data.keys() else True

    
    def __str__(self):
        return self.to_string()
    
    def to_string(self):
        content = ""
        step_content = self.step_obj.step if self.step_obj.step else self.step_obj.sample_step
        content += step_content.replace("\n", "")
        if "(*)" not in content and "(!)" not in content:
            if not self.generated:
                ## add a (*) to the end of the printed step if ungenerated step
                content+=" (*)"
            if len(self.missing_reqs) > 0:
                ## add a (!) to the end of the printed step if requirements missing
                content+=" (!)"
            if self.error:
                if len(self.error) > 0:
                    content+=" (!)"
        else:
            if self.generated:
                content = content.replace("(*)", "")
            if not len(self.missing_reqs) > 0:
                ## add a (!) to the end of the printed step if requirements missing
                content = content.replace("(!)", "")
        return content

    def if_child_exists(self, child_id):
        def check_child_exists(step_children : List[StepContainer], id):
            check = False
            for child in step_children:
                print("JIPO:", child.id, id)
                if child.id == id:
                    check = True
                    break
                else:
                    check = check_child_exists(child.children, id)
            return check
        if self.id == child_id:
            return True
        else:
            return check_child_exists(self.children, child_id)

