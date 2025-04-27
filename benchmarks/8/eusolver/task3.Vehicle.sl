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
			; Vehicle
			(Color x StartColor)
			(Type x StartType)
        ))

        ; terminals
		;Vehicle
		(StartColor String ("Yellow" "Orange" "Green" "Gray" "Red" "Blue" "White" "Golden" "Brown" "Black"))
		(StartType String ("Sedan" "Suv" "Van" "Hatchback" "MPV" "Pickup" "Bus" "Truck" "Estate" "Motor"))
    )
)

; I/O
; +
(declare-var x1 OBJ)
(declare-var x4 OBJ)
(declare-var x9 OBJ)
(declare-var x10 OBJ)
(declare-var x23 OBJ)
; -
(declare-var x2 OBJ)
(declare-var x6 OBJ)
(declare-var x7 OBJ)
(declare-var x15 OBJ)
(declare-var x22 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 1, "cls": "Vehicle", "Color": "Red", "Type": "Hatchback"}) true))
(constraint (= (Respect {"id": 4, "cls": "Vehicle", "Color": "Black", "Type": "MPV"}) true))
(constraint (= (Respect {"id": 9, "cls": "Vehicle", "Color": "Black", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 10, "cls": "Vehicle", "Color": "White", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 23, "cls": "Vehicle", "Color": "Blue", "Type": "Hatchback"}) true))

(constraint (= (Respect {"id": 2, "cls": "Vehicle", "Color": "Black", "Type": "Hatchback"}) false))
(constraint (= (Respect {"id": 6, "cls": "Vehicle", "Color": "Gray", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 7, "cls": "Vehicle", "Color": "Green", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 15, "cls": "Vehicle", "Color": "Blue", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 22, "cls": "Vehicle", "Color": "Gray", "Type": "Hatchback"}) false))

(check-synth)
