import sys
from typing import Optional
import tkinter as tk

def parse_glm_vector(value: str) -> list[str]:
    first_open_par = value.find("(")
    last_close_par = value.rfind(")")
    if value.startswith("dvec"):
        return value[first_open_par+1:last_close_par].split(", ")

def parse_glm_matrix(value: str) -> list[list[str]]:
    first_open_par = value.find("(")
    last_close_par = value.rfind(")")
    if value.startswith("dmat"):
        columns = value[first_open_par+1:last_close_par].split("), (")
        return [list(col.strip("() ").split(", ")) for col in columns]

def to_wolfram_alpha(value: str) -> Optional[str]:
    glm_vec = parse_glm_vector(value)
    if glm_vec:
        return "{"+", ".join("{"+x+"}" for x in glm_vec) + "}"

    glm_mat = parse_glm_matrix(value)
    if glm_mat:
        return "{"+", ".join("{"+", ".join(row)+"}" for row in glm_mat)+"}"

    return None


def to_geogebra(value: str) -> Optional[str]:
    first_open_par = value.find("(")
    last_close_par = value.rfind(")")
    if value.startswith("dvec3"):
        return "Vector("+value[first_open_par:last_close_par+1]+")"
    elif value.startswith("dvec4") or value.startswith("dmat"):
        return to_wolfram_alpha(value)
    return None


def to_latex(value: str) -> Optional[str]:
    glm_vec = parse_glm_vector(value)
    if glm_vec:
        glm_mat = [glm_vec]
    else:
        glm_mat = parse_glm_matrix(value)
    if glm_mat:
        words = [r"\begin{pmatrix}"]
        for row in zip(*glm_mat):
            words.append("&".join(row))
            words.append(r"\\")
        del words[-1]
        words.append(r"\end{pmatrix}")
        return "".join(words)

    return None


def create_copy_func(value: str):
    def func():
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()
    return func


def update_values_if_needed():
    current_value = root.clipboard_get()
    global last_value
    if current_value != last_value:
        last_value = current_value

        for child in root.winfo_children():
            child.destroy()

        for i, (name, func) in enumerate(TRANSFORMERS):
            try:
                result = func(current_value)
            except:
                result = None
            if result is not None:
                name_label = tk.Label(text=name)
                value_label = tk.Label(text=result)
                copy_button = tk.Button(text="Copy", command=create_copy_func(result))

                name_label.grid(row=i, column=0)
                value_label.grid(row=i, column=1)
                copy_button.grid(row=i, column=2)
    root.after(100, update_values_if_needed)


def window_closed():
    root.destroy()
    sys.exit()


TRANSFORMERS = [
    ("Raw value", lambda x: x),
    ("Wolfram Alpha", to_wolfram_alpha),
    ("GeoGebra", to_geogebra),
    ("LaTeX", to_latex),
]

MAX_NAME_LENGTH = max(len(tr[0]) for tr in TRANSFORMERS)


root = tk.Tk()
root.title("Clipboard data Transformer")

last_value = None

root.protocol("WM_DELETE_WINDOW", window_closed)

root.after(0, update_values_if_needed)
tk.mainloop()
