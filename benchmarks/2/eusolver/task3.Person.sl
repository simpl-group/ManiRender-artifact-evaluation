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
		(StartAge Int (24 27 31 35 37))
    )
)

; I/O
; +
(declare-var x1 OBJ)
(declare-var x2 OBJ)
(declare-var x3 OBJ)
(declare-var x6 OBJ)
; -
(declare-var x4 OBJ)
(declare-var x5 OBJ)
(declare-var x7 OBJ)
(declare-var x8 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 1, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 2, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 3, "cls": "Person", "Male": True, "Age": 27, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 6, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))

(constraint (= (Respect {"id": 4, "cls": "Person", "Male": False, "Age": 37, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 5, "cls": "Person", "Male": True, "Age": 31, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperPlaid", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 7, "cls": "Person", "Male": True, "Age": 24, "Orientation": "Back", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 8, "cls": "Person", "Male": True, "Age": 35, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": True, "LongSleeve": False, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))

(check-synth)
