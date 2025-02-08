import json

## Representation of values
# Integer: ("int", value)
# Set: ("set", predicate_id, P(x))
# Predicate: ("predicate", id)
# Bool: ("bool", True/False)

class Evaluator:
    def __init__(self):
        self.id_table = {}
        self.predicate_id = None

    def val_to_str(self, val):
        if val == "void":
            return "void"
        if val[0] == "int":
            return str(val[1])
        if val[0] == "bool":
            return "true" if val[1] else "false"
        if val[0] == "predicate":
            return val[1]
        if val[0] == "set":
            return "{} {}: {} {}".format("{", val[1], self.prop_to_str(val[2]), "}")
        if val[0] == "U":
            return "{} U {}".format(self.val_to_str(val[1]), self.val_to_str(val[2]))
        if val[0] == "I":
            return "{} I {}".format(self.val_to_str(val[1]), self.val_to_str(val[2]))
        return self.prop_to_str(val)
    
    def prop_to_str(self, prop):
        if prop[0] in [">", "<", "=", "@"]:
            prop1 = self.val_to_str(prop[1])
            prop2 = self.val_to_str(prop[2])
            return "{} {} {}".format(prop1, prop[0], prop2)
        if prop[0] in ["&", "|", "!"]:
            return "({} {} {})".format(self.prop_to_str(prop[1]), prop[0], self.prop_to_str(prop[2]))
    
    def simplify_val(self, obj):
        if obj["value"] == "void":
            pass
        else:
            obj["value"] = self.val_to_str(obj["value"])
        if "children" in obj.keys():
            for child in obj["children"]:
                self.simplify_val(child)

    def eval_predicate(self, predicate):
        if predicate[0] in ["<", ">", "="]:
            value1 = predicate[1][1]
            value2 = predicate[2][1]
            if predicate[0] == "<":
                return value1 < value2
            if predicate[0] == ">":
                return value1 > value2
            if predicate[0] == "=":
                return value1 == value2
        if predicate[0] in ["&", "|"]:
            prop1 = self.eval_predicate(predicate[1])
            prop2 = self.eval_predicate(predicate[2])
            if predicate[0] == "&":
                return prop1 and prop2
            if predicate[0] == "|":
                return prop1 or prop2
        if predicate[0] == "!":
            return not self.eval_predicate(predicate[1])
        if predicate[0] == "@":
            return self.judge_in(predicate[1][1], predicate[2])
    
    def judge_in(self, val, set_item):
        if set_item[0] == "set":
            return self.judge_in_(val, set_item[2])
        val1 = self.judge_in(val, set_item[1])
        val2 = self.judge_in(val, set_item[2])
        if set_item[0] == "U":
            return val1 or val2
        else:
            return val1 and val2

    def judge_in_(self, val, set_prop):
        if set_prop[0] in ["<", ">", "="]:
            if set_prop[1][0] == "predicate":
                value1 = val
            else:
                value1 = set_prop[1][1]
            if set_prop[2][0] == "predicate":
                value2 = val
            else:
                value2 = set_prop[2][1]
            if set_prop[0] == "<":
                return value1 < value2
            if set_prop[0] == ">":
                return value1 > value2
            if set_prop[0] == "=":
                return value1 == value2
        if set_prop[0] in ["&", "|"]:
            prop1 = self.judge_in_(val, set_prop[1])
            prop2 = self.judge_in_(val, set_prop[2])
            if set_prop[0] == "&":
                return prop1 and prop2
            if set_prop[0] == "|":
                return prop1 or prop2
        if set_prop[0] == "!":
            return not self.judge_in_(val, set_prop[1])
        if set_prop[0] == "@":
            return self.judge_in_(val, set_prop[2])

    def move_children(self, obj):
        tmp = obj["children"]
        del obj["children"]
        obj["children"] = tmp

    def set_void(self, obj):
        obj["value"] = "void"
    
    def set_id(self, obj, id_value):
        obj["value"] = "void"
        self.id_table[obj["lexeme"]] = id_value

    def evaluate_T(self, T_obj):
        self.set_void(T_obj)
        self.set_void(T_obj["children"][0])
        self.move_children(T_obj)
        return "void"

    def evaluate_E(self, E_obj):
        children = E_obj["children"]
        if len(children) == 1:
            E_obj["value"] = self.evaluate_Ep(children[0])
        else:
            value1 = self.evaluate_E(children[0])
            value2 = self.evaluate_Ep(children[2])
            self.set_void(children[1])
            op = children[1]["token"]
            if op == "U":
                E_obj["value"] = ("U", value1, value2)
            if op == "+":
                E_obj["value"] = ("int", value1[1] + value2[1])
            if op == "-":
                E_obj["value"] = ("int", value1[1] - value2[1])
        self.move_children(E_obj)
        return E_obj["value"]

    def evaluate_Ep(self, Ep_obj):
        children = Ep_obj["children"]
        if len(children) == 1:
            Ep_obj["value"] = self.evaluate_Epp(children[0])
        else:
            value1 = self.evaluate_Ep(children[0])
            value2 = self.evaluate_Epp(children[2])
            self.set_void(children[1])
            op = children[1]["token"]
            if op == "I":
                Ep_obj["value"] = ("I", value1, value2)
            if op == "*":
                Ep_obj["value"] = ("int", value1[1] * value2[1])
        self.move_children(Ep_obj)
        return Ep_obj["value"]

    def evaluate_Epp(self, Epp_obj):
        children = Epp_obj["children"]
        if len(children) == 1:
            if children[0]["token"] == "id":
                if children[0]["lexeme"] in self.id_table.keys():
                    Epp_obj["value"] = self.id_table[children[0]["lexeme"]]
                elif children[0]["lexeme"] == self.predicate_id:
                    Epp_obj["value"] = ("predicate", children[0]["lexeme"])
                self.set_void(children[0])
            else:
                Epp_obj["value"] = ("int", int(children[0]["lexeme"]))
                children[0]["value"] = ("int", int(children[0]["lexeme"]))
        elif len(children) == 3:
            self.set_void(children[0])
            Epp_obj["value"] = self.evaluate_E(children[1])
            self.set_void(children[2])
        elif len(children) == 4:
            self.set_void(children[0])
            self.predicate_id = children[1]["children"][0]["lexeme"]
            z_val = self.evaluate_Z(children[1])
            p_val = self.evaluate_P(children[2])
            self.set_void(children[3])
            Epp_obj["value"] = ("set", self.predicate_id, p_val)
            self.predicate_id = None
        self.move_children(Epp_obj)
        return Epp_obj["value"]
    
    def evaluate_P(self, P_obj):
        children = P_obj["children"]
        if len(children) == 1:
            P_obj["value"] = self.evaluate_Pp(children[0])
        else:
            value1 = self.evaluate_P(children[0])
            self.set_void(children[1])
            value2 = self.evaluate_Pp(children[2])
            P_obj["value"] = ("|", value1, value2)
        self.move_children(P_obj)
        return P_obj["value"]
    
    def evaluate_Pp(self, Pp_obj):
        children = Pp_obj["children"]
        if len(children) == 1:
            Pp_obj["value"] = self.evaluate_Ppp(children[0])
        else:
            value1 = self.evaluate_Pp(children[0])
            self.set_void(children[1])
            value2 = self.evaluate_Ppp(children[2])
            Pp_obj["value"] = ("&", value1, value2)
        self.move_children(Pp_obj)
        return Pp_obj["value"]

    def evaluate_Ppp(self, Ppp_obj):
        children = Ppp_obj["children"]
        if len(children) == 1:
            Ppp_obj["value"] = self.evaluate_R(children[0])
        elif len(children) == 2:
            self.set_void(children[0])
            value = self.evaluate_R(children[1])
            Ppp_obj["value"] = ("!", value)
        else:
            self.set_void(children[0])
            Ppp_obj["value"] = self.evaluate_P(children[1])
            self.set_void(children[2])
        self.move_children(Ppp_obj)
        return Ppp_obj["value"]
        
    def evaluate_R(self, R_obj):
        children = R_obj["children"]
        value1 = self.evaluate_E(children[0])
        value2 = self.evaluate_E(children[2])
        self.set_void(children[1])
        op = children[1]["token"]
        R_obj["value"] = (op, value1, value2)
        # if value1[0] == "predicate" or value2[0] == "predicate":
        #     R_obj["value"] = (op, value1, value2)
        # else:
        #     if op == "<":
        #         R_obj["value"] = ("bool", value1[1] < value2[1])
        #     if op == ">":
        #         R_obj["value"] = ("bool", value1[1] > value2[1])
        #     if op == "=":
        #         R_obj["value"] = ("bool", value1[1] == value2[1])
        #     if op == "@":
        #         R_obj["value"] = ("bool", self.judge_in(value1[1], value2[2]))
        self.move_children(R_obj)
        return R_obj["value"]

    def evaluate_S(self, S_obj):
        children = S_obj["children"]
        if len(children) == 3:
            self.evaluate_Dp(children[0])
            S_obj["value"] = self.evaluate_C(children[1])
            self.set_void(children[2])
        else:
            S_obj["value"] = self.evaluate_C(children[0])
            self.set_void(children[1])
        self.move_children(S_obj)
        result_type = S_obj["value"][0]
        result = S_obj["value"]
        self.simplify_val(S_obj)
        if result_type == "set":
            result = ("set", S_obj["value"])
        return result
    
    def evaluate_Dp(self, Dp_obj):
        children = Dp_obj["children"]
        if len(children) == 1:
            self.evaluate_D(children[0])
        else:
            self.evaluate_D(children[0])
            self.evaluate_Dp(children[1])
        Dp_obj["value"] = "void"
        self.move_children(Dp_obj)
        return "void"
    
    def evaluate_D(self, D_obj):
        children = D_obj["children"]
        self.set_void(children[0])
        self.evaluate_T(children[1])
        self.set_void(children[3])
        value = self.evaluate_E(children[4])
        self.set_void(children[5])
        self.set_id(children[2], value)
        D_obj["value"] = "void"
        self.move_children(D_obj)
        return "void"
    
    def evaluate_C(self, C_obj):
        children = C_obj["children"]
        self.set_void(children[0])
        C_obj["value"] = self.evaluate_A(children[1])
        self.move_children(C_obj)
        return C_obj["value"]

    def evaluate_A(self, A_obj):
        children = A_obj["children"]
        if children[0]["name"] == "E":
            A_obj["value"] = self.evaluate_E(children[0])
        else:
            A_obj["value"] = self.evaluate_P(children[0])
            A_obj["value"] = ("bool", self.eval_predicate(A_obj["value"]))
        self.move_children(A_obj)
        return A_obj["value"]
    
    def evaluate_Z(self, Z_obj):
        children = Z_obj["children"]
        self.set_void(children[0])
        self.set_void(children[1])
        Z_obj["value"] = ("predicate", Z_obj["children"][0]["lexeme"])
        self.move_children(Z_obj)
        return "void"
    

def evaluating(parser_out, evaluate_out):
    with open(parser_out, "r") as f:
        json_obj = json.load(f)
    evaluator = Evaluator()
    try:
        result = evaluator.evaluate_S(json_obj)
        print("({}) {}".format(*result))
        with open(evaluate_out, "w") as f:
            json.dump(json_obj, f, indent=2)
    except:
        print("Value Error!")
        with open(evaluate_out, "w") as f:
            json.dump({}, f)