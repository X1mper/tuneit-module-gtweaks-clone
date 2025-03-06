import subprocess
import re
import sys

MACOS_ORDER = ["close", "minimize", "maximize"]
WINDOWS_ORDER = ["minimize", "maximize", "close"]

def get_button_side():
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.wm.preferences", "button-layout"],
        capture_output=True, text=True
    )
    layout = result.stdout.strip().strip("'")
    left_part = layout.split(":")[0].replace("appmenu", "").strip(", ")

    print("true" if not left_part else "false")
    return "true" if not left_part else "false"

def set_button_side(target_side=True):
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.wm.preferences", "button-layout"],
        capture_output=True, text=True
    )
    current_layout = result.stdout.strip().strip("'")
    appmenu_side = "left" if "appmenu" in current_layout.split(":")[0] else "right"
    
    parts = current_layout.split(":")
    buttons = []
    for part in parts:
        for el in part.split(","):
            if el.strip() and el.strip() != "appmenu":
                buttons.append(el.strip())
    
    ordered = []
    pattern = MACOS_ORDER if not target_side else WINDOWS_ORDER
    for btn in pattern:
        if btn in buttons:
            ordered.append(btn)
    
    new_left = []
    new_right = []
    if appmenu_side == "left":
        new_left.append("appmenu")
        if not target_side:
            new_left.extend(ordered)
        else:
            new_right.extend(ordered)
    else:
        new_right.append("appmenu")
        if target_side:
            new_right.extend(ordered)
        else:
            new_left.extend(ordered)
    
    new_layout = f"{','.join(new_left).strip(',')}:{','.join(new_right).strip(',')}"
    new_layout = re.sub(r":+", ":", new_layout)
    new_layout = re.sub(r"^:|:$", "", new_layout)
    new_layout = re.sub(r",+", ",", new_layout)
    
    subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "button-layout", new_layout])

def has_button(button):
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.wm.preferences", "button-layout"],
        capture_output=True, text=True
    )
    exists = "true" if button in result.stdout else "false"
    print(exists)

def toggle_button(button, state):
    state = str(state).lower() == "true" if isinstance(state, str) else state
    current_side = get_button_side() == "true"
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.wm.preferences", "button-layout"],
        capture_output=True, text=True
    )
    current_layout = result.stdout.strip().strip("'")
    
    if state:
        parts = current_layout.split(":")
        found = any(button in part for part in parts)
        if not found:
            if len(parts) > 1:
                parts[1] += f",{button}"
            else:
                parts.append(button)
            new_layout = ":".join(parts)
            subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "button-layout", new_layout])
        set_button_side(current_side)
    else:
        parts = [",".join([e for e in part.split(",") if e.strip() != button]) for part in current_layout.split(":")]
        new_layout = ":".join(parts).replace(",,", ",").strip(":")
        subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.preferences", "button-layout", new_layout])

def close(state):
    toggle_button("close", state)

def minimize(state):
    toggle_button("minimize", state)

def maximize(state):
    toggle_button("maximize", state)

def toggle_side():
    current_side = get_button_side() == "true"
    set_button_side(not current_side)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [function] [args...]")
        sys.exit(1)
        
    func_name = sys.argv[1]
    func = globals().get(func_name)
    
    if not func:
        print(f"Function {func_name} not found")
        sys.exit(1)
        
    try:
        if func_name == "has_button":
            if len(sys.argv) < 3:
                print("Missing button name for has_button")
                sys.exit(1)
            func(sys.argv[2])
        else:
            args = []
            for arg in sys.argv[2:]:
                if arg.lower() in ["true", "false"]:
                    args.append(arg.lower() == "true")
                else:
                    args.append(arg)
            func(*args)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)