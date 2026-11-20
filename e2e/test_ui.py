"""End-to-end UI tests against the built frontend + real backend + fake LLM."""
import os
import pathlib
import re
import tempfile

import pytest
from playwright.sync_api import Page, expect, sync_playwright

BASE = os.environ["E2E_BASE"]
API = os.environ["E2E_API"]
PY = 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))\n'
TMP = pathlib.Path(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        yield b
        b.close()


@pytest.fixture
def ctx(browser):
    c = browser.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True)
    c.grant_permissions(["clipboard-read", "clipboard-write"], origin=BASE)
    block_external_fonts(c)
    yield c
    c.close()


def block_external_fonts(context):
    """Serve Google Fonts as empty CSS so a flaky network can't fail tests."""
    context.route(re.compile(r"https://fonts\.(googleapis|gstatic)\.com/.*"),
                  lambda r: r.fulfill(status=200, content_type="text/css", body=""))


@pytest.fixture
def page(ctx):
    pg = ctx.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and pg.errors.append(m.text))
    yield pg
    assert pg.errors == [], f"console errors: {pg.errors}"


def goto_app(page: Page, section="convert"):
    page.goto(f"{BASE}/#/app/{section}")
    page.wait_for_load_state("networkidle")


def type_source(page: Page, code: str):
    page.locator("textarea.code-area").fill(code)
    page.locator("textarea.code-area").dispatch_event("input")


def convert(page: Page, target="rust"):
    page.select_option("#tgt-lang", target)
    page.locator(".head-actions .btn-primary").click()
    expect(page.locator(".head-actions .btn-primary")).to_contain_text("Convert", timeout=10000)
    expect(page.locator(".head-actions .btn-primary")).not_to_contain_text("Converting", timeout=10000)


# ------------------------------------------------------------------ landing
def test_landing_renders_and_ctas_route(page):
    page.goto(BASE + "/#/")
    expect(page).to_have_title(re.compile("Code Converter"))
    expect(page.locator("h1")).to_contain_text("14 languages")
    for text, hash_ in [("Start converting", "#/app/convert"), ("Batch convert files", "#/app/batch"),
                        ("Open app", "#/app/convert"), ("Browse setup guides", "#/app/guides")]:
        page.goto(BASE + "/#/")
        page.get_by_role("link", name=text).first.click()
        expect(page).to_have_url(BASE + "/" + hash_)
        expect(page.locator(".sidebar")).to_be_visible()


def test_landing_nav_section_links_scroll(page):
    page.goto(BASE + "/#/")
    for name, sid in [("Features", "features"), ("How it works", "how"), ("Languages", "languages")]:
        page.locator(".nav-links").get_by_text(name).click()
        page.wait_for_timeout(700)
        top = page.evaluate(f"document.getElementById('{sid}').getBoundingClientRect().top")
        assert -5 < top < 120, f"{sid} not scrolled into view (top={top})"
    assert page.url == BASE + "/#/"  # in-page links must not break routing


@pytest.mark.parametrize("width,gap", [(1440, 16), (1000, 16), (390, 12)])
def test_landing_nav_is_inset(browser, width, gap):
    pg = browser.new_page(viewport={"width": width, "height": 800})
    block_external_fonts(pg)
    pg.goto(BASE + "/#/")
    for scroll in (0, 1500):
        pg.evaluate(f"window.scrollTo(0,{scroll})"); pg.wait_for_timeout(200)
        r = pg.evaluate("document.querySelector('.nav-inner').getBoundingClientRect().toJSON()")
        assert r["left"] >= gap and width - r["right"] >= gap and 8 <= r["top"] <= 14, r
    pg.close()


def test_landing_demo_code_has_no_ligature_font_trick(page):
    page.goto(BASE + "/#/")
    lig = page.evaluate("getComputedStyle(document.querySelector('.preview pre')).fontVariantLigatures")
    assert lig == "none"


# ---------------------------------------------------------------- converter
def test_provider_status_card(page):
    goto_app(page)
    expect(page.locator(".provider-card")).to_contain_text("DemoGW connected")
    expect(page.locator(".provider-card")).to_contain_text("org/coder-32b")


def test_convert_disabled_until_ready_and_autodetect(page):
    goto_app(page)
    btn = page.locator(".head-actions .btn-primary")
    expect(btn).to_be_disabled()
    type_source(page, PY)
    expect(page.locator("#src-lang")).to_have_value("python")
    expect(btn).to_be_disabled()  # still no target
    page.select_option("#tgt-lang", "rust")
    expect(btn).to_be_enabled()


def test_target_options_follow_valid_pairs(page):
    goto_app(page)
    page.select_option("#src-lang", "python")
    opts = page.locator("#tgt-lang option:not([disabled])").evaluate_all("o => o.map(x => x.value)")
    assert "python" not in opts and "rust" in opts and "sql" not in opts
    page.select_option("#src-lang", "sql")
    opts = page.locator("#tgt-lang option:not([disabled])").evaluate_all("o => o.map(x => x.value)")
    assert sorted(opts) == ["drizzle", "prisma"]


def test_example_button(page):
    goto_app(page)
    expect(page.get_by_role("button", name="Example")).to_be_disabled()
    page.select_option("#src-lang", "golang")
    page.get_by_role("button", name="Example").click()
    assert "package main" in page.locator("textarea.code-area").input_value() or "func" in page.locator("textarea.code-area").input_value()


def test_streaming_convert_updates_output_stats_history(page):
    goto_app(page)
    type_source(page, PY)
    page.select_option("#tgt-lang", "rust")
    page.locator(".head-actions .btn-primary").click()
    expect(page.locator(".streaming")).to_be_visible(timeout=3000)       # mid-stream indicator
    partial = page.locator(".code-out").inner_text(timeout=3000)
    expect(page.locator(".code-out")).to_contain_text("fn main()", timeout=10000)
    assert len(partial) < len(page.locator(".code-out").inner_text())     # it really streamed
    expect(page.locator(".streaming")).to_be_hidden()
    out = page.locator(".code-out").inner_text()
    assert "n <= 1" in out and "Error" not in out
    expect(page.locator(".code-out .hljs-keyword").first).to_be_visible()  # highlighted
    expect(page.locator(".stat").nth(1).locator("strong")).to_have_text("11")
    expect(page.locator(".nav-item", has_text="History").locator(".nav-count")).to_have_text("1")


def test_copy_and_download(page):
    goto_app(page)
    type_source(page, PY); convert(page)
    page.locator(".pane").nth(1).get_by_role("button", name="Copy").click()
    expect(page.locator(".pane").nth(1).get_by_role("button", name="Copied")).to_be_visible()
    assert "fn fibonacci" in page.evaluate("navigator.clipboard.readText()")
    with page.expect_download() as d:
        page.get_by_role("button", name="Download").click()
    assert d.value.suggested_filename == "converted.rs"
    assert "fn main()" in pathlib.Path(d.value.path()).read_text()


def test_keyboard_shortcuts(page):
    goto_app(page)
    type_source(page, PY); page.select_option("#tgt-lang", "rust")
    page.keyboard.press("Control+Enter")
    expect(page.locator(".code-out")).to_contain_text("fn main()", timeout=10000)
    expect(page.locator(".streaming")).to_be_hidden()
    with page.expect_download() as d:
        page.keyboard.press("Control+d")
    assert d.value.suggested_filename == "converted.rs"
    page.keyboard.press("Control+e")
    expect(page.locator(".explanation")).to_contain_text("Overview", timeout=10000)


def test_explain_panel_renders_and_escapes_html(page):
    goto_app(page)
    type_source(page, PY)
    page.get_by_role("button", name="Explain").click()
    panel = page.locator(".explanation")
    expect(panel).to_contain_text("Overview", timeout=10000)
    expect(panel.locator("h4")).to_have_count(4)
    expect(panel.locator(".li")).to_have_count(2)
    expect(panel.locator("strong", has_text="fibonacci(n)")).to_be_visible()
    expect(panel.locator("img")).to_have_count(0)                 # injected tag not rendered
    expect(panel).to_contain_text('<img src=x onerror=')           # shown as text instead
    assert page.evaluate("window.__xss") is None
    page.locator(".panel-head", has_text="Code explanation").get_by_role("button").click()
    expect(panel).to_have_count(0)


def test_setup_panel(page):
    goto_app(page)
    type_source(page, PY); page.select_option("#tgt-lang", "rust")
    page.get_by_role("button", name="Setup").click()
    expect(page.locator(".panel-head h3", has_text="Rust setup")).to_be_visible()
    expect(page.locator(".cmd code").first).to_contain_text("cargo")


def test_swap_moves_output_into_source(page):
    goto_app(page)
    swap = page.get_by_role("button", name="Swap languages")
    expect(swap).to_be_disabled()
    type_source(page, PY); convert(page)
    swap.click()
    expect(page.locator("#src-lang")).to_have_value("rust")
    expect(page.locator("#tgt-lang")).to_have_value("python")
    assert page.locator("textarea.code-area").input_value().startswith("use std::io;")
    expect(page.locator(".empty-out")).to_be_visible()


def test_layout_toggle(page):
    goto_app(page)
    expect(page.locator(".editors")).to_have_class(re.compile("split"))
    page.get_by_title("Stacked").click()
    expect(page.locator(".editors")).to_have_class(re.compile("single"))
    a, b = [page.locator(".pane").nth(i).bounding_box() for i in (0, 1)]
    assert b["y"] > a["y"] and abs(a["x"] - b["x"]) < 2
    page.get_by_title("Side by side").click()
    a, b = [page.locator(".pane").nth(i).bounding_box() for i in (0, 1)]
    assert b["x"] > a["x"]


def test_upload_file_sets_language(page):
    f = TMP / "main.go"; f.write_text('package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("hi")\n}\n')
    goto_app(page)
    page.locator(".toolbar input[type=file]").set_input_files(str(f))
    expect(page.locator("#src-lang")).to_have_value("golang")
    expect(page.locator(".stat").first).to_contain_text("main.go")
    assert "fmt.Println" in page.locator("textarea.code-area").input_value()


def test_drag_and_drop_file(page):
    goto_app(page)
    page.evaluate("""() => {
      const dt = new DataTransfer();
      dt.items.add(new File(['fn main() { println!("x"); }'], 'lib.rs', {type: 'text/plain'}));
      const pane = document.querySelector('.pane');
      pane.dispatchEvent(new DragEvent('dragover', {dataTransfer: dt, bubbles: true}));
      pane.dispatchEvent(new DragEvent('drop', {dataTransfer: dt, bubbles: true}));
    }""")
    expect(page.locator("#src-lang")).to_have_value("rust")
    expect(page.locator(".drop-hint")).to_have_count(0)


def test_too_large_and_empty_file_errors(page):
    big = TMP / "big.py"; big.write_text("x" * (1024 * 1024 + 10))
    empty = TMP / "empty.py"; empty.write_text("   ")
    goto_app(page)
    page.locator(".toolbar input[type=file]").set_input_files(str(big))
    expect(page.locator(".alert")).to_contain_text("too large")
    page.locator(".toolbar input[type=file]").set_input_files(str(empty))
    expect(page.locator(".alert")).to_contain_text("empty")
    page.get_by_role("button", name="Dismiss").click()
    expect(page.locator(".alert")).to_have_count(0)


def test_syntax_warning_cancel_and_proceed(page):
    goto_app(page)
    type_source(page, "print((1)\n"); page.select_option("#src-lang", "python"); page.select_option("#tgt-lang", "rust")
    page.once("dialog", lambda d: d.dismiss())
    page.locator(".head-actions .btn-primary").click()
    expect(page.locator(".alert")).to_contain_text("Unmatched parentheses")
    expect(page.locator(".empty-out")).to_be_visible()
    page.once("dialog", lambda d: d.accept())
    page.locator(".head-actions .btn-primary").click()
    expect(page.locator(".code-out")).to_contain_text("fn main()", timeout=10000)


def test_comment_with_keyword_converts_without_syntax_dialog(page):
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    goto_app(page)
    type_source(page, '# loop for each item\nitems = [1, 2]  # (note\nprint("if x (")\n')
    page.select_option("#src-lang", "python")
    convert(page)
    assert dialogs == []
    expect(page.locator(".code-out")).to_contain_text("fn main()")


def test_upstream_failure_before_output_shows_banner(page):
    goto_app(page)
    type_source(page, "x = 'FAIL_ME'\n"); page.select_option("#src-lang", "python"); convert(page)
    expect(page.locator(".alert")).to_contain_text("DemoGW conversion failed")
    expect(page.locator(".alert")).not_to_contain_text('{"detail"')   # parsed, not raw JSON
    expect(page.locator(".empty-out")).to_be_visible()                 # nothing in the output pane
    expect(page.locator(".nav-item", has_text="History").locator(".nav-count")).to_have_count(0)
    # Chrome itself logs every non-2xx response; that 502 is the expected one.
    page.errors[:] = [e for e in page.errors if "status of 502" not in e]


def test_upstream_failure_mid_stream_keeps_partial_output(page):
    goto_app(page)
    type_source(page, "x = 'FAIL_MID'\n"); page.select_option("#src-lang", "python"); convert(page)
    alert = page.locator(".alert")
    expect(alert).to_contain_text("DemoGW stopped mid-conversion")
    expect(alert).to_contain_text("incomplete")
    out = page.locator(".code-out")
    expect(out).to_contain_text("use std::io;")
    expect(out).not_to_contain_text("STREAM_ERROR")
    expect(out).not_to_contain_text("stopped mid-conversion")
    expect(page.locator(".nav-item", has_text="History").locator(".nav-count")).to_have_count(0)


def test_clear_resets(page):
    goto_app(page)
    type_source(page, PY); page.select_option("#tgt-lang", "rust")
    page.locator(".pane").first.get_by_role("button", name="Clear").click()
    assert page.locator("textarea.code-area").input_value() == ""
    expect(page.locator("#src-lang")).to_have_value("")
    expect(page.locator(".stat").first.locator("strong")).to_have_text("0")


def test_backend_offline_is_reported(browser):
    c = browser.new_context(viewport={"width": 1440, "height": 900})
    block_external_fonts(c)
    c.route(API + "/**", lambda r: r.abort())
    pg = c.new_page()
    pg.goto(BASE + "/#/app/convert")
    expect(pg.locator(".provider-card")).to_contain_text("Backend offline")
    type_source(pg, PY); pg.select_option("#tgt-lang", "rust")
    pg.locator(".head-actions .btn-primary").click()
    expect(pg.locator(".alert")).to_contain_text("Failed to fetch")
    pg.get_by_role("button", name="Explain").click()
    expect(pg.locator(".alert")).to_be_visible()
    c.close()


# ------------------------------------------------------------------ history
def make_history(page, n_targets=("rust", "golang")):
    goto_app(page)
    for t in n_targets:
        type_source(page, PY); page.select_option("#src-lang", "python"); convert(page, t)


def test_history_table_search_filter_open_delete_clear(page):
    make_history(page)
    page.locator(".nav-item", has_text="History").click()
    expect(page).to_have_url(BASE + "/#/app/history")
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(2)
    expect(rows.first).to_contain_text("Go")                       # newest first
    expect(page.locator(".stat").first.locator("strong")).to_have_text("2")
    page.select_option(".table-tools select", "rust")
    expect(rows).to_have_count(1); expect(rows.first).to_contain_text("Rust")
    page.select_option(".table-tools select", "")
    page.get_by_placeholder("Search code or language").fill("nothing-matches-this")
    expect(page.locator(".empty")).to_contain_text("No conversions match")
    page.get_by_placeholder("Search code or language").fill("fibonacci")
    expect(rows).to_have_count(2)
    rows.nth(1).get_by_role("button", name="Open").click()          # open the Rust one
    expect(page).to_have_url(BASE + "/#/app/convert")
    expect(page.locator("#tgt-lang")).to_have_value("rust")
    expect(page.locator(".code-out")).to_contain_text("fn main()")
    page.locator(".nav-item", has_text="History").click()
    rows.first.get_by_role("button", name="Delete").click()
    expect(rows).to_have_count(1)
    expect(page.locator(".nav-item", has_text="History").locator(".nav-count")).to_have_text("1")
    page.once("dialog", lambda d: d.accept())
    page.get_by_role("button", name="Clear all").click()
    expect(page.locator(".empty")).to_contain_text("No conversions yet")


def test_history_persists_across_reload_and_caps_at_10(page):
    goto_app(page)
    page.evaluate("""() => localStorage.setItem('code_conversion_history', JSON.stringify(
      Array.from({length: 10}, (_, i) => ({id: String(i), sourceLanguage: 'python', targetLanguage: 'java',
        sourceCode: 'print(' + i + ')', convertedCode: 'class A {}', timestamp: Date.now() - i * 1000}))))""")
    page.reload(); page.wait_for_load_state("networkidle")
    type_source(page, PY); convert(page)
    page.locator(".nav-item", has_text="History").click()
    expect(page.locator("tbody tr")).to_have_count(10)
    expect(page.locator("tbody tr").first).to_contain_text("Rust")


# -------------------------------------------------------------------- batch
def test_batch_full_flow(page):
    a = TMP / "a.py"; a.write_text(PY)
    b = TMP / "b.py"; b.write_text("x = 'FAIL_ME'\n")
    goto_app(page, "batch")
    convert_btn = page.locator(".head-actions .btn-primary")
    expect(convert_btn).to_be_disabled()
    page.locator(".drop input[type=file]").set_input_files([str(a), str(b)])
    expect(page.locator("tbody tr")).to_have_count(2)
    expect(page.locator(".lang-picker select").first).to_have_value("python")   # auto-detected
    expect(convert_btn).to_be_disabled()
    page.locator(".lang-picker select").nth(1).select_option("rust")
    expect(convert_btn).to_have_text(re.compile("Convert 2 files"))
    convert_btn.click()
    expect(page.locator("tbody tr").first.locator(".badge")).to_have_text("Converted", timeout=15000)
    expect(page.locator("tbody tr").nth(1).locator(".badge")).to_have_text("Failed")
    expect(page.locator(".table-foot")).to_contain_text("1 succeeded")
    expect(page.locator(".table-foot")).to_contain_text("1 failed")
    with page.expect_download() as d:
        page.locator("tbody tr").first.get_by_role("button", name="Download").click()
    assert d.value.suggested_filename == "a_converted.rs"
    assert "fn main()" in pathlib.Path(d.value.path()).read_text()
    with page.expect_download():
        page.get_by_role("button", name="Download all").click()
    page.locator("tbody tr").nth(1).get_by_role("button", name="Remove").click()
    expect(page.locator("tbody tr")).to_have_count(1)
    page.get_by_role("button", name="Clear").click()
    expect(page.locator("tbody tr")).to_have_count(0)


def test_batch_limits(page):
    files = []
    for i in range(12):
        f = TMP / f"f{i}.py"; f.write_text(f"print({i})\n"); files.append(str(f))
    big = TMP / "huge.py"; big.write_text("x" * (1024 * 1024 + 5))
    goto_app(page, "batch")
    page.locator(".drop input[type=file]").set_input_files([str(big)] + files)
    expect(page.locator(".alert")).to_contain_text("huge.py")
    expect(page.locator("tbody tr")).to_have_count(10)
    expect(page.locator(".toolbar .badge")).to_have_text("10/10 files")


def test_batch_inherits_converter_language_pair(page):
    goto_app(page)
    page.select_option("#src-lang", "java"); page.select_option("#tgt-lang", "golang")
    page.locator(".nav-item", has_text="Batch convert").click()
    expect(page.locator(".lang-picker select").first).to_have_value("java")
    expect(page.locator(".lang-picker select").nth(1)).to_have_value("golang")


# ------------------------------------------------------------------- guides
def test_guides(page):
    goto_app(page, "guides")
    for lang, word in [("Rust", "cargo"), ("Go", "go"), ("Python", "pip")]:
        page.locator(".lang-list button", has_text=re.compile(rf"^\S+\s*{re.escape(lang)}$")).click()
        expect(page.locator(".guide-card header h3")).to_have_text(lang)
        expect(page.locator(".cmd code").first).to_contain_text(word)
    page.locator(".cmd").first.get_by_title("Copy").click()
    assert "pip" in page.evaluate("navigator.clipboard.readText()")


# --------------------------------------------------------- theme / routing
def test_dark_mode_toggle_persists(page):
    goto_app(page)
    page.get_by_role("button", name="Dark mode").click()
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    page.reload()
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == bg == "rgb(14, 14, 17)"
    page.get_by_role("button", name="Light mode").click()
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(245, 245, 246)"


def test_system_dark_preference(browser):
    c = browser.new_context(color_scheme="dark"); block_external_fonts(c); pg = c.new_page()
    pg.goto(BASE + "/#/")
    assert pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(14, 14, 17)"
    c.close()


def test_routing_back_button_and_unknown_section(page):
    page.goto(BASE + "/#/")
    page.get_by_role("link", name="Start converting").click()
    page.locator(".nav-item", has_text="History").click()
    page.go_back(); expect(page).to_have_url(BASE + "/#/app/convert")
    page.go_back(); expect(page.locator(".hero")).to_be_visible()
    page.goto(BASE + "/#/app/nope")
    expect(page.locator("h1")).to_have_text("Converter")


def test_state_survives_section_switch(page):
    goto_app(page)
    type_source(page, PY); page.select_option("#tgt-lang", "rust")
    page.locator(".nav-item", has_text="Setup guides").click()
    page.locator(".nav-item", has_text="Converter").click()
    assert page.locator("textarea.code-area").input_value() == PY
    expect(page.locator("#tgt-lang")).to_have_value("rust")


# ------------------------------------------------------------------- mobile
@pytest.mark.parametrize("route", ["#/", "#/app/convert", "#/app/batch", "#/app/history", "#/app/guides"])
def test_mobile_no_horizontal_scroll(browser, route):
    pg = browser.new_page(viewport={"width": 390, "height": 844})
    block_external_fonts(pg)
    pg.goto(BASE + "/" + route); pg.wait_for_load_state("networkidle")
    assert pg.evaluate("document.documentElement.scrollWidth") <= 390
    pg.close()


def test_mobile_menu(browser):
    pg = browser.new_page(viewport={"width": 390, "height": 844})
    block_external_fonts(pg)
    pg.goto(BASE + "/#/app/convert")
    expect(pg.locator(".sidebar")).not_to_be_in_viewport()
    pg.get_by_role("button", name="Open menu").click()
    expect(pg.locator(".sidebar")).to_be_in_viewport()
    pg.locator(".sidebar .nav-item", has_text="History").click()
    expect(pg).to_have_url(BASE + "/#/app/history")
    pg.wait_for_timeout(300)
    expect(pg.locator(".sidebar")).not_to_be_in_viewport()
    pg.get_by_role("button", name="Open menu").click()
    pg.locator(".scrim").click(position={"x": 370, "y": 400})
    pg.wait_for_timeout(300)
    expect(pg.locator(".sidebar")).not_to_be_in_viewport()
    pg.close()
