import json

class TypeChecker:
    # create an empty identifier table
    def __init__(self):
        self.id_table = {}
        self.predicate_id = None

    # Move 'children' within the given object
    def move_children(self, obj):
        tmp = obj["children"]
        del obj["children"]
        obj["children"] = tmp

    def set_void(self, obj):
        obj["type"] = "void"
    
    def set_id(self, obj, id_type):
        obj["type"] = "void"
        self.id_table[obj["lexeme"]] = id_type

    # Check the type for the object related to 'T'
    def check_T(self, T_obj):
        children = T_obj["children"]
        if children[0]["token"] == "set":
            T_obj["type"] = "set"
        else:
            T_obj["type"] = "integer"
        self.set_void(children[0])
        self.move_children(T_obj)
        return T_obj["type"]

    # Check the type for the object related to 'E'
    def check_E(self, E_obj):
        children = E_obj["children"]
        if len(children) == 1:
            E_obj["type"] = self.check_Ep(children[0])
        else:
            type1 = self.check_E(children[0])
            type2 = self.check_Ep(children[2])
            self.set_void(children[1])
            op = children[1]["token"]
            if op == "U":
                if type1 == "set" and type2 == "set":
                    E_obj["type"] = "set"
                else:
                    raise Exception()
            if op in ["+", "-"]:
                if type1 == "integer" and type2 == "integer":
                    E_obj["type"] = "integer"
                else:
                    raise Exception()
        self.move_children(E_obj)
        return E_obj["type"]

    # Check the type for the object related to 'Ep'
    def check_Ep(self, Ep_obj):
        children = Ep_obj["children"]
        if len(children) == 1:
            Ep_obj["type"] = self.check_Epp(children[0])
        else:
            type1 = self.check_Ep(children[0])
            type2 = self.check_Epp(children[2])
            self.set_void(children[1])
            op = children[1]["token"]
            if op == "I":
                if type1 == "set" and type2 == "set":
                    Ep_obj["type"] = "set"
                else:
                    raise Exception()
            if op == "*":
                if type1 == "integer" and type2 == "integer":
                    Ep_obj["type"] = "integer"
                else:
                    raise Exception()
        self.move_children(Ep_obj)
        return Ep_obj["type"]

    # Check the type for the object related to 'Epp'
    def check_Epp(self, Epp_obj):
        children = Epp_obj["children"]
        if len(children) == 1:
            if children[0]["token"] == "id":
                if children[0]["lexeme"] in self.id_table.keys():
                    Epp_obj["type"] = self.id_table[children[0]["lexeme"]]
                elif children[0]["lexeme"] == self.predicate_id:
                    Epp_obj["type"] = "integer"
                else:
                    raise Exception()
                self.set_void(children[0])
            else:
                Epp_obj["type"] = "integer"
                children[0]["type"] = "integer"
        elif len(children) == 3:
            self.set_void(children[0])
            Epp_obj["type"] = self.check_E(children[1])
            self.set_void(children[2])
        elif len(children) == 4:
            self.set_void(children[0])
            self.predicate_id = children[1]["children"][0]["lexeme"]
            self.check_Z(children[1])
            self.check_P(children[2])
            self.set_void(children[3])
            self.predicate_id = None
            Epp_obj["type"] = "set"
        self.move_children(Epp_obj)
        return Epp_obj["type"]
    
    # Check the type for the object related to 'P'
    def check_P(self, P_obj):
        children = P_obj["children"]
        if len(children) == 1:
            self.check_Pp(children[0])
        else:
            self.check_P(children[0])
            self.set_void(children[1])
            self.check_Pp(children[2])
        P_obj["type"] = "predicate"
        self.move_children(P_obj)
        return "predicate"
    
    # Check the type for the object related to 'Pp'
    def check_Pp(self, Pp_obj):
        children = Pp_obj["children"]
        if len(children) == 1:
            self.check_Ppp(children[0])
        else:
            self.check_Pp(children[0])
            self.set_void(children[1])
            self.check_Ppp(children[2])
        Pp_obj["type"] = "predicate"
        self.move_children(Pp_obj)
        return "predicate"

    # Check the type for the object related to 'Ppp'
    def check_Ppp(self, Ppp_obj):
        children = Ppp_obj["children"]
        if len(children) == 1:
            self.check_R(children[0])
        elif len(children) == 2:
            self.set_void(children[0])
            self.check_R(children[1])
        else:
            self.set_void(children[0])
            self.check_P(children[1])
            self.set_void(children[2])
        Ppp_obj["type"] = "predicate"
        self.move_children(Ppp_obj)
        return "predicate"

    # Check the type for the object related to 'R'    
    def check_R(self, R_obj):
        children = R_obj["children"]
        type1 = self.check_E(children[0])
        type2 = self.check_E(children[2])
        self.set_void(children[1])
        op = children[1]["token"]
        if op == "@":
            if type1 != "integer" or type2 != "set":
                raise Exception()
        else:
            if type1 != "integer" or type2 != "integer":
                raise Exception()
        R_obj["type"] = "relation"
        self.move_children(R_obj)
        return "relation"

    # Check the type for the object related to 'S'
    def check_S(self, S_obj):
        children = S_obj["children"]
        if len(children) == 3:
            self.check_Dp(children[0])
            self.check_C(children[1])
            self.set_void(children[2])
            S_obj["type"] = "program"
        else:
            self.check_C(children[0])
            self.set_void(children[1])
            S_obj["type"] = "calculation"
        self.move_children(S_obj)
        return S_obj["type"]
    
    def check_Dp(self, Dp_obj):
        children = Dp_obj["children"]
        if len(children) == 1:
            self.check_D(children[0])
        else:
            self.check_D(children[0])
            self.check_Dp(children[1])
        Dp_obj["type"] = "declarations"
        self.move_children(Dp_obj)
        return "declarations"
    
    # Check the type for the object related to 'D'
    def check_D(self, D_obj):
        children = D_obj["children"]
        self.set_void(children[0])
        id_type = self.check_T(children[1])
        self.set_id(children[2], id_type)
        self.set_void(children[3])
        expr_type = self.check_E(children[4])
        self.set_void(children[5])
        if id_type != expr_type:
            raise Exception()
        D_obj["type"] = "declaration"
        self.move_children(D_obj)
        return "declaration"
    
    # Check the type for the object related to 'C'
    def check_C(self, C_obj):
        children = C_obj["children"]
        self.set_void(children[0])
        self.check_A(children[1])
        C_obj["type"] = "calculation"
        self.move_children(C_obj)
        return "calculation"

    # Check the type for the object related to 'A'
    def check_A(self, A_obj):
        children = A_obj["children"]
        if children[0]["name"] == "E":
            self.check_E(children[0])
        else:
            self.check_P(children[0])
        A_obj["type"] = "calculation"
        self.move_children(A_obj)
        return "calculation"
    
    # Check the type for the object related to 'Z'
    def check_Z(self, Z_obj):
        children = Z_obj["children"]
        self.set_void(children[0])
        self.set_void(children[1])
        Z_obj["type"] = "void"
        self.move_children(Z_obj)
        return "void"
    

def type_checking(parser_out, typing_out):
    with open(parser_out, "r") as f:
        json_obj = json.load(f)
    checker = TypeChecker()
    try:
        checker.check_S(json_obj)
        with open(typing_out, "w") as f:
            json.dump(json_obj, f, indent=2)
    except:
        print("Type Error!")
        with open(typing_out, "w") as f:
            json.dump({}, f)