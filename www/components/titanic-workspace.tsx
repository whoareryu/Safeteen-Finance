"use client";

import TitanicDataUpload from "@/components/titanic-data-upload";

export default function TitanicWorkspace() {
  return (
    <div className="titanic-workspace border-t border-border bg-background">
      <div className="mx-auto w-full max-w-3xl px-4 py-8 sm:px-6 md:py-10">
        <TitanicDataUpload />
      </div>
    </div>
  );
}
