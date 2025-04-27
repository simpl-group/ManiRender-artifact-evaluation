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
		(StartAge Int (15 16 17 18 19 20 21 22 23 24 25 27 28 32 34 36 37 39 42))
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
(declare-var x10 OBJ)
(declare-var x11 OBJ)
(declare-var x35 OBJ)
(declare-var x39 OBJ)
(declare-var x43 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 1, "cls": "Person", "Male": True, "Age": 39, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 2, "cls": "Person", "Male": True, "Age": 34, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 3, "cls": "Person", "Male": True, "Age": 32, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))
(constraint (= (Respect {"id": 6, "cls": "Person", "Male": True, "Age": 24, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))

(constraint (= (Respect {"id": 4, "cls": "Person", "Male": True, "Age": 19, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 10, "cls": "Person", "Male": True, "Age": 25, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 11, "cls": "Person", "Male": False, "Age": 42, "Orientation": "Front", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 35, "cls": "Person", "Male": True, "Age": 36, "Orientation": "Front", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "UpperStride", "BottomStyle": "BottomStripe", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 39, "cls": "Person", "Male": True, "Age": 27, "Orientation": "Front", "Glasses": False, "Hat": True, "HoldObjectsInFront": True, "Bag": "NoBag", "TopStyle": "UpperLogo", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 43, "cls": "Person", "Male": True, "Age": 37, "Orientation": "Side", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) false))

(check-synth)
