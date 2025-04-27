(set-logic OBJ)

; ∀ x ∈ POS. Respect(x) = true
; ∀ x ∈ NEG. Respect(x) = false
(synth-fun Respect ((x OBJ)) Bool
    (
        (Start Bool (
            (Color x StartColor)
            (Type x StartGenre)
            (Or Start Start)
            (And Start Start)
            (Not Start)
        ))
        (StartColor String ("Red" "Green")) ; color
        (StartGenre String ("Sedan" "MPV")) ; genre
    )
)

; I/O
; POS: {x1: {Red, Sedan}}
; NEG: {x2: {Green, MPV}}
;(declare-var x1 OBJ)
;(declare-var x2 OBJ)

; facts
(constraint (= (Respect {"id": 1, "color": "Red", "genre": "Sedan"}) true))
(constraint (= (Respect {"id": 2, "color": "Green", "genre": "Sedan"}) false))
(constraint (= (Respect {"id": 3, "color": "Red", "genre": "MPV"}) false))

;(define-fun Respect ((x Obj)) Bool
;     (Intersect (IsType x "Sedan") (IsColor x "Red")))

(check-synth)