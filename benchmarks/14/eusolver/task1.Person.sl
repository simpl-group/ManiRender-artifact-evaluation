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
		(StartAge Int (22 23 24 27 28 29 30 31 32 34 35 36 38 40 41 45 49 55))
    )
)

; I/O
; +
(declare-var x1 OBJ)
(declare-var x3 OBJ)
(declare-var x4 OBJ)
(declare-var x7 OBJ)
(declare-var x8 OBJ)
(declare-var x10 OBJ)
(declare-var x20 OBJ)
(declare-var x23 OBJ)
(declare-var x25 OBJ)
; -
(declare-var x5 OBJ)
(declare-var x9 OBJ)
(declare-var x11 OBJ)
(declare-var x12 OBJ)
(declare-var x13 OBJ)
(declare-var x14 OBJ)
(declare-var x15 OBJ)
(declare-var x16 OBJ)
(declare-var x17 OBJ)
(declare-var x18 OBJ)
(declare-var x19 OBJ)
(declare-var x21 OBJ)
(declare-var x24 OBJ)

; facts
; userdefined args = {}
(constraint (= (Respect {"id": 1, "cls": "Person", "Male": True, "Age": 22, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 3, "cls": "Person", "Male": True, "Age": 27, "Orientation": "Side", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 4, "cls": "Person", "Male": False, "Age": 29, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 7, "cls": "Person", "Male": True, "Age": 40, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 8, "cls": "Person", "Male": True, "Age": 31, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 10, "cls": "Person", "Male": False, "Age": 24, "Orientation": "Side", "Glasses": False, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 20, "cls": "Person", "Male": True, "Age": 32, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 23, "cls": "Person", "Male": False, "Age": 23, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "HandBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) true))
(constraint (= (Respect {"id": 25, "cls": "Person", "Male": False, "Age": 29, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "BackPack", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": False, "SkirtDress": False, "Boots": False}) true))

(constraint (= (Respect {"id": 5, "cls": "Person", "Male": True, "Age": 38, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 9, "cls": "Person", "Male": True, "Age": 41, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "HandBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 11, "cls": "Person", "Male": False, "Age": 35, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": True, "Bag": "HandBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": False, "SkirtDress": True, "Boots": False}) false))
(constraint (= (Respect {"id": 12, "cls": "Person", "Male": False, "Age": 28, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": True, "Bag": "HandBag", "TopStyle": "UpperSplice", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 13, "cls": "Person", "Male": True, "Age": 38, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 14, "cls": "Person", "Male": True, "Age": 40, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 15, "cls": "Person", "Male": False, "Age": 45, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 16, "cls": "Person", "Male": True, "Age": 36, "Orientation": "Side", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 17, "cls": "Person", "Male": False, "Age": 30, "Orientation": "Back", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "UpperPlaid", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": False}) false))
(constraint (= (Respect {"id": 18, "cls": "Person", "Male": True, "Age": 49, "Orientation": "Back", "Glasses": True, "Hat": True, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 19, "cls": "Person", "Male": True, "Age": 55, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 21, "cls": "Person", "Male": False, "Age": 34, "Orientation": "Side", "Glasses": False, "Hat": False, "HoldObjectsInFront": False, "Bag": "ShoulderBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": False, "LongCoat": True, "Trousers": False, "Shorts": True, "SkirtDress": False, "Boots": True}) false))
(constraint (= (Respect {"id": 24, "cls": "Person", "Male": True, "Age": 31, "Orientation": "Side", "Glasses": True, "Hat": False, "HoldObjectsInFront": False, "Bag": "NoBag", "TopStyle": "NoTopStyle", "BottomStyle": "NoBottomStyle", "ShortSleeve": False, "LongSleeve": True, "LongCoat": False, "Trousers": True, "Shorts": False, "SkirtDress": False, "Boots": True}) false))

(check-synth)
