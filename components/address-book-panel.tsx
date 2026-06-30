"use client";

import { useEffect, useState } from "react";
import { Loader2, UserPlus } from "lucide-react";
import { fetchContacts, type ApiContact } from "@/lib/chef-address";
import AddressBookUploadModal from "@/components/address-book-upload-modal";

type Props = {
  onSelect: (email: string) => void;
};

export default function AddressBookPanel({ onSelect }: Props) {
  const [contacts, setContacts] = useState<ApiContact[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const reload = () => {
    setLoading(true);
    fetchContacts()
      .then(setContacts)
      .catch(() => setContacts([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { reload(); }, []);

  return (
    <>
      <div className="flex h-full flex-col rounded-2xl border border-black/10 bg-white shadow-sm">
        {/* 패널 헤더 */}
        <div className="flex items-center justify-between border-b border-black/[0.06] px-4 py-3">
          <span className="text-sm font-semibold text-[#1d1d1f]">주소록</span>
          <button
            type="button"
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-1.5 rounded-full bg-primary px-3 py-1.5 text-xs font-medium text-white"
          >
            <UserPlus className="h-3.5 w-3.5" />
            등록
          </button>
        </div>

        {/* 연락처 목록 */}
        <ul className="flex-1 overflow-y-auto divide-y divide-black/[0.04]">
          {loading ? (
            <li className="flex items-center justify-center px-4 py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </li>
          ) : contacts.length === 0 ? (
            <li className="px-4 py-8 text-center text-sm text-muted-foreground">
              등록된 연락처가 없습니다.
              <br />
              <span className="text-xs">CSV 파일을 업로드해 추가하세요.</span>
            </li>
          ) : (
            contacts.map((c) => (
              <li key={c.email}>
                <button
                  type="button"
                  onClick={() => onSelect(c.email)}
                  className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-[#f5f5f7]"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                    {c.name.charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-[#1d1d1f]">{c.name}</p>
                    <p className="truncate text-xs text-muted-foreground">{c.email}</p>
                    {c.company && (
                      <p className="truncate text-xs text-muted-foreground">{c.company}</p>
                    )}
                  </div>
                </button>
              </li>
            ))
          )}
        </ul>
      </div>

      {showModal && (
        <AddressBookUploadModal
          onClose={() => setShowModal(false)}
          onSaved={() => {
            setShowModal(false);
            reload();
          }}
        />
      )}
    </>
  );
}
