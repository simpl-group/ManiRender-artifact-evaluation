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
			; Person
			(Male x)
			(AgeLess x StartAge)
			(AgeGreater x StartAge)
			(AgeEq x StartAge)
			(Orientation x StartOrientation)
			(Glasses x)
			(Hat x)
			(HoldObjectsInFront x)
			(Bag x StartBag)
			(TopStyle x StartTopStyle)
			(BottomStyle x StartBottomStyle)
			(ShortSleeve x)
			(LongSleeve x)
			(LongCoat x)
			(Trousers x)
			(Shorts x)
			(SkirtDress x)
			(Boots x)
        ))

        ; terminals
		;Person
		(StartOrientation String ("Front" "Back" "Side"))
		(StartBag String ("BackPack" "ShoulderBag" "HandBag" "NoBag"))
		(StartTopStyle String ("UpperStride" "UpperLogo" "UpperPlaid" "UpperSplice" "NoTopStyle"))
		(StartBottomStyle String ("BottomStripe" "BottomPattern" "NoBottomStyle"))
		(StartAge Int (21 22 23 24 25 31 34 35 36 37 39 40 42 45 50 53 54 55 62 65))
    )
)

; I/O
; +
(declare-var x1 OBJ)
(declare-var x4 OBJ)
(declare-var x8 OBJ)
(declare-var x9 OBJ)
; -
(declare-var x2 OBJ)
(declare-var x5 OBJ)
(declare-var x10 OBJ)
(declare-var x16 OBJ)
(declare-var x25 OBJ)
(declare-var x31 OBJ)
(declare-var x32 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 1, "cls": "Person", "Male": False, "Age": 54, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) true))
(constraint (= (Respect {"id": 4, "cls": "Person", "Male": False, "Age": 37, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "BottomPattern", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) true))
(constraint (= (Respect {"id": 8, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) true))
(constraint (= (Respect {"id": 9, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "BottomPattern", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) true))

(constraint (= (Respect {"id": 2, "cls": "Person", "Male": False, "Age": 23, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 5, "cls": "Person", "Male": False, "Age": 22, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 10, "cls": "Person", "Male": False, "Age": 65, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 16, "cls": "Person", "Male": False, "Age": 40, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "UpperSplice", "BottomStyle": "BottomPattern", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 25, "cls": "Person", "Male": False, "Age": 36, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 31, "cls": "Person", "Male": True, "Age": 50, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 32, "cls": "Person", "Male": False, "Age": 39, "Orientation": "Front", "Glasses": True, "Hat": False, "HoldObjectsInFront": True, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))

(check-synth)
