import { mkdir, writeFile } from "fs/promises";
import path from "path";
import { NextResponse } from "next/server";

const MAX_BYTES = 15 * 1024 * 1024; // 15MB

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!file || !(file instanceof Blob)) {
      return NextResponse.json(
        { ok: false, error: "파일이 없습니다." },
        { status: 400 }
      );
    }
    const name = (file as File).name?.toLowerCase() ?? "";
    if (!name.endsWith(".csv")) {
      return NextResponse.json(
        { ok: false, error: "CSV 파일만 업로드할 수 있습니다." },
        { status: 400 }
      );
    }
    const buf = Buffer.from(await file.arrayBuffer());
    if (buf.length > MAX_BYTES) {
      return NextResponse.json(
        { ok: false, error: "파일이 너무 큽니다. (최대 15MB)" },
        { status: 400 }
      );
    }
    const dir = path.join(process.cwd(), "uploads", "titanic");
    await mkdir(dir, { recursive: true });
    const dest = path.join(dir, "titanic.csv");
    await writeFile(dest, buf);
    return NextResponse.json({
      ok: true,
      message: "titanic.csv 저장 완료",
      savedAs: "uploads/titanic/titanic.csv",
      bytes: buf.length,
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "알 수 없는 오류";
    return NextResponse.json(
      { ok: false, error: message },
      { status: 500 }
    );
  }
}
