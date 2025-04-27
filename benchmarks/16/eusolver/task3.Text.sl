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
			(EndsWith x StartEndsWith)
        ))

        ; terminals
		;Text
		(StartLength Int (4 7 10 12 15))
		(StartEndsWith String ("St" "Ave"))
    )
)

; I/O
; +
(declare-var x16 OBJ)
(declare-var x17 OBJ)
(declare-var x20 OBJ)
; -
(declare-var x14 OBJ)
(declare-var x15 OBJ)

; facts
; userdefined args = {'Text': {'EndsWith': ['St', 'Ave']}}
(constraint (= (Respect {"id": 16, "cls": "Text", "Context": "Eighth Ave", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 10}) true))
(constraint (= (Respect {"id": 17, "cls": "Text", "Context": "West 33rd St", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 12}) true))
(constraint (= (Respect {"id": 20, "cls": "Text", "Context": "Eighth Ave", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 10}) true))

(constraint (= (Respect {"id": 14, "cls": "Text", "Context": "ONE WAY", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 7}) false))
(constraint (= (Respect {"id": 15, "cls": "Text", "Context": "Joe Louis Plaza", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 15}) false))

(check-synth)
