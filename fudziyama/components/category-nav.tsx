"use client";

import * as React from "react";

import type { Category } from "@/lib/products";
import { cn } from "@/lib/utils";

interface CategoryNavProps {
  categories: Category[];
}

/**
 * Липкая панель категорий. Активная категория подсвечивается автоматически
 * по мере прокрутки (scroll-spy через IntersectionObserver).
 */
export function CategoryNav({ categories }: CategoryNavProps) {
  const [activeId, setActiveId] = React.useState<string>(categories[0]?.id ?? "");
  const navRef = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    const sections = categories
      .map((c) => document.getElementById(`category-${c.id}`))
      .filter((el): el is HTMLElement => el !== null);

    if (sections.length === 0) return;

    // Активной считается секция, пересекающая горизонтальную полосу
    // сразу под липкой панелью.
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible.length > 0) {
          setActiveId(visible[0].target.id.replace("category-", ""));
        }
      },
      { rootMargin: "-120px 0px -60% 0px" }
    );

    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, [categories]);

  // Держим активную «таблетку» в видимой зоне при горизонтальном скролле на телефоне.
  React.useEffect(() => {
    const activeButton = navRef.current?.querySelector<HTMLElement>(
      `[data-category="${activeId}"]`
    );
    activeButton?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
      inline: "center",
    });
  }, [activeId]);

  const scrollToCategory = (id: string) => {
    setActiveId(id);
    document
      .getElementById(`category-${id}`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <nav
      ref={navRef}
      className="sticky top-16 z-40 border-b bg-background/90 backdrop-blur-md"
      aria-label="Категории меню"
    >
      <div className="container flex gap-2 overflow-x-auto py-3 no-scrollbar">
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            data-category={category.id}
            onClick={() => scrollToCategory(category.id)}
            className={cn(
              "shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-colors",
              activeId === category.id
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            )}
          >
            {category.title}
          </button>
        ))}
      </div>
    </nav>
  );
}
