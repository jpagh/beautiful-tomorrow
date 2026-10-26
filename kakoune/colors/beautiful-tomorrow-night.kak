# Beautiful UI — Tomorrow Night (named Tomorrow Dark in the extension)
# Adapted from swashata/vscode-beautiful-ui (MIT); see ../themes/tomorrow/LICENSE.
# Translucent VS Code UI colors are composited onto the editor background.

# Syntax
face global value rgb:DE935F
face global type rgb:F0C674
face global variable rgb:C5C8C6
face global module rgb:F0C674
face global function rgb:81A2BE
face global string rgb:B5BD68
face global keyword rgb:B294BB
face global operator rgb:E9B36D
face global attribute rgb:DE935F+i
face global comment rgb:969896+i
face global documentation comment
face global meta rgb:CC6666
face global builtin rgb:CC6666+i

# Markup
face global title rgb:CC6666+b
face global header title
face global mono rgb:B294BB
face global block rgb:C5C8C6
face global link rgb:81A2BE+u
face global bullet rgb:DE935F
face global list bullet
face global bold rgb:E9B36D+b
face global italic rgb:E9B36D+i

# Editor and selections (preserve syntax foregrounds)
face global Default rgb:C5C8C6,rgb:1D1F21
face global PrimarySelection default,rgb:373b41+g
face global SecondarySelection default,rgb:2B2D2E+g
face global PrimaryCursor rgb:1D1F21,rgb:DE935F+fg
face global SecondaryCursor rgb:1D1F21,rgb:969896+fg
face global PrimaryCursorEol PrimaryCursor
face global SecondaryCursorEol SecondaryCursor
face global LineNumbers rgb:4A4C4D
face global LineNumberCursor rgb:6D6E6F+b
face global LineNumbersWrapped LineNumbers
face global MatchingChar default,rgb:4F4B39+b
face global Whitespace rgb:303233+f
face global WrapMarker rgb:4A4C4D
face global BufferPadding rgb:4A4C4D

# Menus and status line
face global MenuForeground rgb:D3D0C8,rgb:454545+b
face global MenuBackground rgb:D3D0C8,rgb:242424
face global MenuInfo rgb:81A2BE
face global Information rgb:D3D0C8,rgb:282828
face global InlineInformation Information
face global Error rgb:F4878A,rgb:1D1D1D+b
face global StatusLine rgb:D2D2D2,rgb:1D1D1D
face global StatusLineMode rgb:FFFFFF,rgb:C34B07+b
face global StatusLineInfo rgb:81A2BE,rgb:1D1D1D
face global StatusLineValue rgb:B5BD68,rgb:1D1D1D+b
face global StatusCursor rgb:1D1F21,rgb:DE935F
face global Prompt rgb:B294BB,rgb:1D1D1D+b

# kakoune-lsp and diff tools
face global DiagnosticError rgb:F4878A
face global DiagnosticWarning rgb:FFD278
face global DiagnosticInfo rgb:81A2BE
face global DiagnosticHint rgb:A5D2A5
face global InlayHint rgb:969896+i
face global InlayCodeLens InlayHint
face global DiffPlus rgb:A5D2A5
face global DiffMinus rgb:F4878A
face global DiffDelta rgb:71A1D0
