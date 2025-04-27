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
(declare-var x2 OBJ)
(declare-var x3 OBJ)
(declare-var x21 OBJ)
; -
(declare-var x1 OBJ)
(declare-var x5 OBJ)
(declare-var x7 OBJ)
(declare-var x10 OBJ)
(declare-var x11 OBJ)
(declare-var x13 OBJ)
(declare-var x28 OBJ)
(declare-var x30 OBJ)
(declare-var x34 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 2, "cls": "Vehicle", "Color": "White", "Type": "Suv"}) true))
(constraint (= (Respect {"id": 3, "cls": "Vehicle", "Color": "Black", "Type": "Sedan"}) true))
(constraint (= (Respect {"id": 21, "cls": "Vehicle", "Color": "White", "Type": "Van"}) true))

(constraint (= (Respect {"id": 1, "cls": "Vehicle", "Color": "Blue", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 5, "cls": "Vehicle", "Color": "Black", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 7, "cls": "Vehicle", "Color": "White", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 10, "cls": "Vehicle", "Color": "Red", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 11, "cls": "Vehicle", "Color": "Black", "Type": "Van"}) false))
(constraint (= (Respect {"id": 13, "cls": "Vehicle", "Color": "Red", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 28, "cls": "Vehicle", "Color": "Gray", "Type": "Sedan"}) false))
(constraint (= (Respect {"id": 30, "cls": "Vehicle", "Color": "Brown", "Type": "Suv"}) false))
(constraint (= (Respect {"id": 34, "cls": "Vehicle", "Color": "Red", "Type": "Hatchback"}) false))

(check-synth)
