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
		(StartAge Int (25 27 28 31 32 34 35 38 41 42 55))
    )
)

; I/O
; +
(declare-var x7 OBJ)
(declare-var x8 OBJ)
; -
(declare-var x5 OBJ)
(declare-var x6 OBJ)
(declare-var x10 OBJ)
(declare-var x11 OBJ)
(declare-var x13 OBJ)
(declare-var x14 OBJ)
(declare-var x16 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 7, "cls": "Person", "Male": True, "Age": 34, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 8, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))

(constraint (= (Respect {"id": 5, "cls": "Person", "Male": True, "Age": 38, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 6, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": True, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 10, "cls": "Person", "Male": True, "Age": 42, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 11, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 13, "cls": "Person", "Male": True, "Age": 41, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 14, "cls": "Person", "Male": True, "Age": 25, "Orientation": "Side", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 16, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))

(check-synth)
