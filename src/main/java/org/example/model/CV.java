package org.example.model;

public class CV {
    private final String filename;
    private final String rawText;
    private boolean approved;

    public CV(String filename, String rawText) {
        if (filename == null || filename.isBlank()) throw new IllegalArgumentException("filename inválido");
        if (rawText == null) rawText = "";
        this.filename = filename;
        this.rawText = rawText;
        this.approved = false;
    }

    public String getFilename() { return filename; }
    public String getRawText() { return rawText; }

    public boolean isApproved() { return approved; }
    public void approve() { this.approved = true; }
    public void reject() { this.approved = false; }
}