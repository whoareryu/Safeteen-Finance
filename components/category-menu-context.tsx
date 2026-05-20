"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

type CategoryMenuContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
  toggle: () => void;
};

const CategoryMenuContext = createContext<CategoryMenuContextValue | null>(null);

export function CategoryMenuProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const toggle = useCallback(() => setOpen((v) => !v), []);

  const value = useMemo(
    () => ({ open, setOpen, toggle }),
    [open, toggle]
  );

  return (
    <CategoryMenuContext.Provider value={value}>
      {children}
    </CategoryMenuContext.Provider>
  );
}

export function useCategoryMenu() {
  const ctx = useContext(CategoryMenuContext);
  if (!ctx) {
    throw new Error("useCategoryMenu must be used within CategoryMenuProvider");
  }
  return ctx;
}

export function useCategoryMenuOptional() {
  return useContext(CategoryMenuContext);
}
