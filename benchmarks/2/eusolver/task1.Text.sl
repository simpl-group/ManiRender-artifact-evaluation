(set-logic OBJ)

; ∀ x ∈ POS. Respect(x) = true
; ∀ x ∈ NEG. Respect(x) = false
(synth-fun Respect ((x OBJ)) Bool
    (
        (Start Bool (
            ; Or/And/Not
            (Or Start Start)
            (And Start Start)
            (Not Start)

            ; userdefined functions
			; Text
			(Empty x)
			(PureNumber x)
			(PureAlphabet x)
			(LengthLess x StartLength)
			(LengthGreater x StartLength)
			(LengthEq x StartLength)
			(In x StartIn)
        ))

        ; terminals
		;Text
		(StartLength Int (0 2 6 7 8 9 10 12 13 16 18 21))
		(StartIn String ("CHINA" "CHINESE" "MOON" "HAPPINESS" "FESTIVAL"))
    )
)

; I/O
; +
(declare-var x15 OBJ)
(declare-var x17 OBJ)
(declare-var x19 OBJ)
(declare-var x23 OBJ)
; -
(declare-var x13 OBJ)
(declare-var x16 OBJ)
(declare-var x20 OBJ)
(declare-var x22 OBJ)
(declare-var x24 OBJ)
(declare-var x25 OBJ)
(declare-var x30 OBJ)

; facts
; userdefined args = {'Text': {'In': ['CHINA', 'CHINESE', 'MOON', 'HAPPINESS', 'FESTIVAL']}}
(constraint (= (Respect {"id": 15, "cls": "Text", "Context": "Chinese Arts & Crafts", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 21}) true))
(constraint (= (Respect {"id": 17, "cls": "Text", "Context": "MOON FESTIVAL", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 13}) true))
(constraint (= (Respect {"id": 19, "cls": "Text", "Context": "HAPPINESS", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 9}) true))
(constraint (= (Respect {"id": 23, "cls": "Text", "Context": "CHINA TRADE CENTER", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 18}) true))

(constraint (= (Respect {"id": 13, "cls": "Text", "Context": "WELCOME", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 7}) false))
(constraint (= (Respect {"id": 16, "cls": "Text", "Context": "WHOLESALE RETAIL", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 16}) false))
(constraint (= (Respect {"id": 20, "cls": "Text", "Context": "CELEBRATE", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 9}) false))
(constraint (= (Respect {"id": 22, "cls": "Text", "Context": "PEKING", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 6}) false))
(constraint (= (Respect {"id": 24, "cls": "Text", "Context": "closing sale", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 12}) false))
(constraint (= (Respect {"id": 25, "cls": "Text", "Context": "STOPPING", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 8}) false))
(constraint (= (Respect {"id": 30, "cls": "Text", "Context": "", "Empty": True, "PureNumber": False, "PureAlphabet": False, "Length": 0}) false))

(check-synth)
