import re

def wrap_buttons(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Wrap the delete 'x' or '×' buttons
    pattern_x = r'(<button type="button" onClick=\{\(\) => set(?:Schedule|Participant|Cost|Documentation)Rows\(.*?\}\)\} className="w-6 h-6 rounded-full bg-red-50 text-red-500 text-xs font-bold">.*?</button>)'
    content = re.sub(pattern_x, r"{user?.role !== 'Dean' && (\n                                \1\n                              )}", content)

    # Wrap the '+ Add ...' buttons
    pattern_add = r'(<button type="button" onClick=\{\(\) => set(?:Schedule|Participant|Cost|Documentation)Rows\(.*?\}\)\} className="text-\[\#2174C3\] font-bold text-sm">\+ Add .*?</button>)'
    # Use lambda to keep exact indentation. Actually, re.sub replaces the entire match.
    # The '+ Add' button might have spaces before it. Let's capture the spaces.
    pattern_add2 = r'^(\s*)(<button type="button" onClick=\{\(\) => set(?:Schedule|Participant|Cost|Documentation)Rows\(.*?\}\)\} className="text-\[\#2174C3\] font-bold text-sm">\+ Add .*?</button>)'
    content = re.sub(pattern_add2, r"\1{user?.role !== 'Dean' && (\n\1  \2\n\1)}", content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

wrap_buttons('c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingMasterPage.jsx')
print("Successfully wrapped buttons")
