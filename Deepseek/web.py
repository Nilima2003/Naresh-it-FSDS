import tkinter as tk
from tkinter import scrolledtext
import subprocess

def run_deepseek(prompt):
    result = subprocess.run(
        ["ollama", "run", "deepseek-r1:1.5b", prompt],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def ask_question(q=None):
    question = q if q else entry.get()
    if not question:
        return

    # Get answer
    answer = run_deepseek(f"Answer this question clearly:\n\n{question}")
    answer_box.delete("1.0", tk.END)
    answer_box.insert(tk.END, answer)

    # Get related
    related_prompt = f"Based on the question '{question}' and its answer '{answer}', suggest 3 related follow-up questions."
    related = run_deepseek(related_prompt).split("\n")

    for widget in related_frame.winfo_children():
        widget.destroy()
    for r in related:
        btn = tk.Button(related_frame, text=r, command=lambda q=r: ask_question(q))
        btn.pack(pady=2, fill="x")

root = tk.Tk()
root.title("Welcome To Deepseek")

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

ask_btn = tk.Button(root, text="Ask", command=lambda: ask_question())
ask_btn.pack()

answer_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=10)
answer_box.pack(pady=10)

related_frame = tk.Frame(root)
related_frame.pack(pady=10)

root.mainloop()