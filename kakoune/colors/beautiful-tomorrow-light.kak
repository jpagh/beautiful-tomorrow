# Beautiful UI — Tomorrow Light
# Adapted from swashata/vscode-beautiful-ui (MIT); see ../themes/tomorrow/LICENSE.
# Translucent VS Code UI colors are composited onto the editor background.

# Syntax
face global value rgb:D2702B
face global type rgb:E9AD35
face global variable rgb:202225
face global module rgb:E9AD35
face global function rgb:5884A9
face global string rgb:737935
face global keyword rgb:946CA1
face global operator rgb:E09432
face global attribute rgb:D2702B+i
face global comment rgb:959795+i
face global documentation comment
face global meta rgb:B83D3D
face global builtin rgb:B83D3D+i

# Markup
face global title rgb:B83D3D+b
face global header title
face global mono rgb:946CA1
face global block rgb:202225
face global link rgb:5884A9+u
face global bullet rgb:D2702B
face global list bullet
face global bold rgb:E09432+b
face global italic rgb:E09432+i

# Editor and selections (preserve syntax foregrounds)
face global Default rgb:282A2E,rgb:FFFFFF
face global PrimarySelection default,rgb:E5E5E5+g
face global SecondarySelection default,rgb:EFEFEF+g
face global PrimaryCursor rgb:FFFFFF,rgb:CC6666+fg
face global SecondaryCursor rgb:FFFFFF,rgb:959795+fg
face global PrimaryCursorEol PrimaryCursor
face global SecondaryCursorEol SecondaryCursor
face global LineNumbers rgb:CCCCCC
face global LineNumberCursor rgb:A5A5A5+b
face global LineNumbersWrapped LineNumbers
face global MatchingChar default,rgb:FCECC7+b
face global Whitespace rgb:E9E9E9+f
face global WrapMarker rgb:CCCCCC
face global BufferPadding rgb:CCCCCC

# Menus and status line
face global MenuForeground rgb:282A2E,rgb:DDDDDD+b
face global MenuBackground rgb:282A2E,rgb:E2E2E2
face global MenuInfo rgb:5884A9
face global Information rgb:282A2E,rgb:E7E7E7
face global InlineInformation Information
face global Error rgb:C44F4F,rgb:E2E2E2+b
face global StatusLine rgb:2D2D2D,rgb:E2E2E2
face global StatusLineMode rgb:FFFFFF,rgb:AC3939+b
face global StatusLineInfo rgb:5884A9,rgb:E2E2E2
face global StatusLineValue rgb:737935,rgb:E2E2E2+b
face global StatusCursor rgb:FFFFFF,rgb:CC6666
face global Prompt rgb:946CA1,rgb:E2E2E2+b

# kakoune-lsp and diff tools
face global DiagnosticError rgb:C44F4F
face global DiagnosticWarning rgb:E19D18
face global DiagnosticInfo rgb:5884A9
face global DiagnosticHint rgb:878F3E
face global InlayHint rgb:959795+i
face global InlayCodeLens InlayHint
face global DiffPlus rgb:878F3E
face global DiffMinus rgb:C44F4F
face global DiffDelta rgb:4C7393
