"use client";

import { ImageUploadIcon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

interface UploadCardDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (file: File) => Promise<void>;
}

export function UploadCardDialog({
  open,
  onOpenChange,
  onUpload,
}: UploadCardDialogProps) {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileSelect(file: File) {
    if (!file.type.startsWith("image/")) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  }

  function handleClose(open: boolean) {
    if (!open) {
      setImageFile(null);
      setPreview(null);
    }
    onOpenChange(open);
  }

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault();
    if (!imageFile) return;
    setIsUploading(true);
    try {
      await onUpload(imageFile);
      handleClose(false);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Card</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div
            className={cn(
              "relative mx-auto flex aspect-[2.5/3.5] w-36 shrink-0 cursor-pointer flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed transition-colors",
              isDragging
                ? "border-foreground bg-muted"
                : "border-muted-foreground/30 hover:border-muted-foreground/60",
            )}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            {preview ? (
              // eslint-disable-next-line @next/next/no-img-element -- blob URL from local file, not optimizable by next/image
              <img
                src={preview}
                alt="Card preview"
                className="absolute inset-0 h-full w-full object-cover"
              />
            ) : (
              <div className="text-muted-foreground flex flex-col items-center gap-1.5 px-2 text-center">
                <HugeiconsIcon
                  icon={ImageUploadIcon}
                  strokeWidth={1.5}
                  className="size-6"
                />
                <span className="text-xs leading-tight">
                  Click or drag image
                </span>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={handleInputChange}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleClose(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!imageFile || isUploading}>
              {isUploading ? "Uploading…" : "Upload"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
