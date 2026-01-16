"""
Command Line Interface for RCT Extraction Pipeline

Provides commands for:
- extract: Extract data from PDFs
- assess: Run Risk of Bias assessment only
- info: Display pipeline configuration
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .pipeline import RCTExtractionPipeline, PipelineConfig, run_pipeline
from .extractor import RCTExtractor, get_model_info, check_grobid_status
from .rob_assessor import assess_rob, get_rob_model_info, ROB_AVAILABLE

app = typer.Typer(
    name="rct-extract",
    help="RCT Extraction Pipeline - Extract structured data from RCT publications",
    add_completion=False,
)

console = Console()


# ============================================================================
# Extract Command
# ============================================================================

@app.command()
def extract(
    input_path: Path = typer.Argument(
        ...,
        help="Path to PDF file or directory containing PDFs",
        exists=True,
    ),
    output_dir: Path = typer.Option(
        Path("./output"),
        "--output", "-o",
        help="Output directory for results",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-n",
        help="Limit number of files to process",
    ),
    no_rob: bool = typer.Option(
        False,
        "--no-rob",
        help="Skip Risk of Bias assessment",
    ),
    extraction_model: str = typer.Option(
        "claude-3-5-sonnet-20241022",
        "--model", "-m",
        help="Extraction model (Claude)",
    ),
    rob_model: str = typer.Option(
        "gpt-4o",
        "--rob-model",
        help="Risk of Bias assessment model (OpenAI)",
    ),
    chunk_size: int = typer.Option(
        2000,
        "--chunk-size",
        help="Document chunk size in characters",
    ),
    chunk_overlap: int = typer.Option(
        400,
        "--chunk-overlap",
        help="Overlap between chunks",
    ),
    grobid_url: str = typer.Option(
        "http://localhost:8070",
        "--grobid-url",
        help="GROBID server URL for section-aware parsing",
    ),
    no_grobid: bool = typer.Option(
        False,
        "--no-grobid",
        help="Disable GROBID (use fallback splitter)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Verbose output",
    ),
):
    """
    Extract structured data from RCT manuscript PDFs.
    
    Process a single PDF or batch of PDFs to extract:
    - Study metadata (title, journal, year, funding)
    - Methodological details (randomization, blinding)
    - Participant information and demographics
    - Intervention and comparator details
    - Outcome measures and results
    - Risk of Bias assessment (RoB 2.0)
    """
    
    # Check GROBID status
    grobid_status = "Disabled" if no_grobid else check_grobid_status(grobid_url)
    grobid_display = "Disabled" if no_grobid else (
        f"[green]Available[/green] ({grobid_url})" if grobid_status.get("available") 
        else f"[yellow]Unavailable[/yellow] (fallback mode)"
    )
    
    console.print(Panel.fit(
        "[bold blue]RCT Extraction Pipeline[/bold blue]\n"
        f"Input: {input_path}\n"
        f"Output: {output_dir}\n"
        f"Model: {extraction_model}\n"
        f"GROBID: {grobid_display}\n"
        f"RoB Assessment: {'Disabled' if no_rob else f'Enabled ({rob_model})'}",
        title="Configuration",
    ))
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure pipeline
    config = PipelineConfig(
        extraction_model=extraction_model,
        rob_model=rob_model,
        run_rob_assessment=not no_rob,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        grobid_url=grobid_url,
        use_grobid=not no_grobid,
    )
    
    pipeline = RCTExtractionPipeline(config)
    
    # Process files
    if input_path.is_file():
        # Single file
        console.print(f"\n[yellow]Processing single file: {input_path.name}[/yellow]")
        result = pipeline.process_single(input_path, output_dir)
        
        # Display result
        _display_extraction_result(result)
        
        # Save result
        output_file = output_dir / f"{input_path.stem}_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"\n[green]Result saved to: {output_file}[/green]")
        
    else:
        # Directory of files
        console.print(f"\n[yellow]Processing directory: {input_path}[/yellow]")
        results = pipeline.process_batch(input_path, output_dir, limit=limit)
        
        # Summary
        success = sum(1 for r in results if r.get("status") == "success")
        console.print(f"\n[green]Processed {len(results)} files[/green]")
        console.print(f"Successful: {success}/{len(results)}")


def _display_extraction_result(result: dict):
    """Display extraction result in a formatted table"""
    table = Table(title="Extraction Result", show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    extraction = result.get("extraction", {})
    
    # Key fields to display
    display_fields = [
        ("Title", extraction.get("title")),
        ("Journal", extraction.get("journalName")),
        ("Year", extraction.get("yearOfPublication")),
        ("Participants", extraction.get("totalParticipants")),
        ("Therapeutic Area", extraction.get("therapeuticArea")),
        ("Randomization", extraction.get("randomization")),
        ("Blinding", extraction.get("blinding")),
        ("Primary Outcome", extraction.get("primaryOutcome")),
    ]
    
    for field, value in display_fields:
        if value is not None:
            table.add_row(field, str(value)[:80])
    
    # RoB results
    if "risk_of_bias" in result:
        rob = result["risk_of_bias"]
        if "overall" in rob:
            table.add_row("RoB Overall", rob["overall"])
    
    console.print(table)


# ============================================================================
# Assess Command (RoB only)
# ============================================================================

@app.command()
def assess(
    manuscript: Path = typer.Argument(
        ...,
        help="Path to manuscript PDF",
        exists=True,
    ),
    model: str = typer.Option(
        "gpt-4o",
        "--model", "-m",
        help="OpenAI model for assessment",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for results (JSON)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Verbose output",
    ),
):
    """
    Run Risk of Bias (RoB 2.0) assessment on a manuscript.
    
    Assesses bias in 5 domains:
    1. Randomization process
    2. Deviations from intended interventions
    3. Missing outcome data
    4. Measurement of the outcome
    5. Selection of reported result
    """
    if not ROB_AVAILABLE:
        console.print("[red]Error: Risk of Bias package not available[/red]")
        raise typer.Exit(1)
    
    console.print(Panel.fit(
        f"[bold blue]Risk of Bias Assessment[/bold blue]\n"
        f"Manuscript: {manuscript.name}\n"
        f"Model: {model}",
        title="RoB 2.0",
    ))
    
    # Run assessment
    with console.status("[bold yellow]Running RoB assessment...[/bold yellow]"):
        result = assess_rob(
            manuscript_path=manuscript,
            model=model,
            verbose=verbose,
        )
    
    # Display results
    table = Table(title="Risk of Bias Assessment", show_header=True)
    table.add_column("Domain", style="cyan")
    table.add_column("Judgment", style="green")
    
    for domain, data in result.get("domains", {}).items():
        judgment = data.get("judgment", "N/A")
        color = "green" if judgment == "Low" else "yellow" if judgment == "Some concerns" else "red"
        table.add_row(domain.replace("_", " ").title(), f"[{color}]{judgment}[/{color}]")
    
    console.print(table)
    
    # Save output
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"\n[green]Results saved to: {output}[/green]")


# ============================================================================
# Info Command
# ============================================================================

@app.command()
def info():
    """Display pipeline configuration and model information."""
    
    # Extraction info
    ext_info = get_model_info()
    
    console.print(Panel.fit(
        "[bold blue]RCT Extraction Pipeline[/bold blue]\n\n"
        "A comprehensive pipeline for extracting structured data from\n"
        "randomized controlled trial (RCT) publications.",
        title="Pipeline Info",
    ))
    
    # LLM Table
    table = Table(title="Large Language Models", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")
    table.add_column("Purpose")
    
    table.add_row(
        "Data Extraction",
        ext_info["extraction_llm"]["provider"],
        ext_info["extraction_llm"]["model"],
        "Extract structured fields from text",
    )
    table.add_row(
        "Embeddings",
        ext_info["embedding_model"]["provider"],
        ext_info["embedding_model"]["model"],
        f"Vector embeddings ({ext_info['embedding_model']['dimensions']}d)",
    )
    
    if ROB_AVAILABLE:
        rob_info = get_rob_model_info()
        table.add_row(
            "Risk of Bias",
            rob_info["llm"]["provider"],
            rob_info["llm"]["default_model"],
            "RoB 2.0 assessment",
        )
    
    console.print(table)
    
    # Processing Table
    proc_table = Table(title="Document Processing", show_header=True)
    proc_table.add_column("Parameter", style="cyan")
    proc_table.add_column("Value", style="green")
    
    proc_table.add_row("Primary Parser", ext_info["document_processing"]["primary"])
    proc_table.add_row("Fallback Parser", ext_info["document_processing"]["fallback"])
    proc_table.add_row("Vector Database", ext_info["vector_database"]["name"])
    proc_table.add_row("Chunk Size", str(ext_info["chunking"]["chunk_size"]))
    proc_table.add_row("Chunk Overlap", str(ext_info["chunking"]["chunk_overlap"]))
    proc_table.add_row("Top-K Retrieval", str(ext_info["retrieval"]["top_k"]))
    
    # Check GROBID status
    grobid_status = check_grobid_status()
    grobid_color = "green" if grobid_status["available"] else "yellow"
    proc_table.add_row(
        "GROBID Status", 
        f"[{grobid_color}]{grobid_status['message']}[/{grobid_color}]"
    )
    
    console.print(proc_table)
    
    # RoB Framework
    if ROB_AVAILABLE:
        rob_info = get_rob_model_info()
        console.print(Panel.fit(
            f"[bold]Framework:[/bold] {rob_info['framework']['name']}\n"
            f"[bold]Reference:[/bold] {rob_info['framework']['reference']}\n\n"
            "[bold]Domains:[/bold]\n" + 
            "\n".join(f"  • {name}: {desc}" for name, desc in rob_info['framework']['domains']),
            title="Risk of Bias (RoB 2.0)",
        ))


# ============================================================================
# GROBID Command
# ============================================================================

@app.command()
def grobid(
    url: str = typer.Option(
        "http://localhost:8070",
        "--url", "-u",
        help="GROBID server URL to check",
    ),
):
    """
    Check GROBID server status and display setup instructions.
    
    GROBID provides section-aware parsing for scientific papers,
    extracting structured sections (Abstract, Methods, Results, etc.)
    for more accurate retrieval.
    """
    console.print(Panel.fit(
        "[bold blue]GROBID Status Check[/bold blue]",
        title="Scientific Paper Parser",
    ))
    
    # Check status
    status = check_grobid_status(url)
    
    if status["available"]:
        console.print(f"\n[green]✓ GROBID is running at {url}[/green]")
        console.print("\nSection-aware parsing is enabled. The pipeline will:")
        console.print("  • Extract paper structure (Abstract, Methods, Results, etc.)")
        console.print("  • Create section-tagged chunks for better retrieval")
        console.print("  • Use targeted queries per section type")
    else:
        console.print(f"\n[yellow]✗ GROBID not available at {url}[/yellow]")
        console.print("\nThe pipeline will use fallback mode (generic text splitting).")
        console.print("\n[bold]To enable GROBID:[/bold]")
        console.print("\n[cyan]Option 1: Docker (recommended)[/cyan]")
        console.print("```bash")
        console.print("docker pull lfoppiano/grobid:0.8.1")
        console.print("docker run -d --name grobid -p 8070:8070 lfoppiano/grobid:0.8.1")
        console.print("```")
        console.print("\n[cyan]Option 2: Use public demo server (rate-limited)[/cyan]")
        console.print("```bash")
        console.print("rct-extract extract paper.pdf --grobid-url https://kermitt2-grobid.hf.space")
        console.print("```")
        console.print("\n[cyan]Option 3: Disable GROBID[/cyan]")
        console.print("```bash")
        console.print("rct-extract extract paper.pdf --no-grobid")
        console.print("```")


# ============================================================================
# Version Command
# ============================================================================

@app.command()
def version():
    """Display version information."""
    console.print("[bold]RCT Extraction Pipeline[/bold] v1.0.0")
    console.print("GitHub: https://github.com/rob-luke/risk-of-bias (RoB fork)")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    app()
