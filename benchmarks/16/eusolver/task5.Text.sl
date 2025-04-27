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
(declare-var x14 OBJ)
; -
(declare-var x19 OBJ)

; facts
; userdefined args = {'Text': {'EndsWith': ['St', 'Ave']}}
(constraint (= (Respect {"id": 14, "cls": "Text", "Context": "ONE WAY", "Empty": False, "PureNumber": False, "PureAlphabet": False, "Length": 7}) true))

(constraint (= (Respect {"id": 19, "cls": "Text", "Context": "TAXI", "Empty": False, "PureNumber": False, "PureAlphabet": True, "Length": 4}) false))

(check-synth)
