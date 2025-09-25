import re
from pylatexenc.latex2text import LatexNodes2Text

latex_to_unicode = {
    '\\bigcup': '⋃', '\\cup': '∪', '\\cap': '∩', '\\subset': '⊂', '\\subseteq': '⊆',
    '\\in': '∈', '\\leq': '≤', '\\geq': '≥', '\\sum': '∑', '\\int': '∫', '\\infty': '∞',
    '\\cdot': '⋅', '\\times': '×', '\\div': '÷', '\\pm': '±', '\\sqrt': '√'
}

greek_letters = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε', 'zeta': 'ζ',
    'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν',
    'xi': 'ξ', 'omicron': 'ο', 'pi': 'π', 'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'upsilon': 'υ',
    'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω'
}

def replace_latex_commands(text):
    for latex_cmd, unicode_symbol in latex_to_unicode.items():
        pattern = r'\\' + re.escape(latex_cmd)
        text = re.sub(pattern, unicode_symbol, text)
    return text

def replace_greek_letters(text):
    for letter, symbol in greek_letters.items():
        text = re.sub(r'\\' + letter, symbol, text)
    return text

def replace_math_expressions(text):
    text = re.sub(r'\\{(.*?)\\}', r'the set of \1', text)
    text = re.sub(r'\\:', ':', text)
    return text

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def process_answer_text(html_content):
    latex_text = LatexNodes2Text().latex_to_text(html_content)
    latex_text = re.sub(r'\$(.*?)\$', r'\1', latex_text)  
    latex_text = replace_latex_commands(latex_text)
    latex_text = replace_greek_letters(latex_text)
    latex_text = replace_math_expressions(latex_text)
    latex_text = remove_html_tags(latex_text)
    return latex_text