import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8854725609:AAENBkemJRROAU59h2mSnKH9OHT1RHVsCp4"

SCAM_DATABASE = {
    "0987654321": {"type": "SĐT", "reason": "Giả danh nhân viên giao hàng nhận tiền cọc."},
    "1234567890": {"type": "STK Ngân hàng", "bank": "Vietcombank", "reason": "Mạo danh công an yêu cầu chuyển tiền."},
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 **Chào mừng bạn đến với Bot kiểm tra lừa đảo!**\n\n"
        "• Nhập **SĐT/STK** để kiểm tra.\n"
        "• Nhập `/report <số> <lý do>` để thêm số lừa đảo mới."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def report_scam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cú pháp: /report <số> <mô tả hình thức lừa đảo>
    if len(context.args) < 2:
        await update.message.reply_text("❌ **Sai cú pháp!**\nVui lòng nhập: `/report <Số_SĐT_hoặc_STK> <Lý_do_lừa_đảo>`\n\nVí dụ: `/report 0911223344 Giả danh Shopee cọc tiền`", parse_mode="Markdown")
        return

    number = re.sub(r"\D", "", context.args[0])
    reason = " ".join(context.args[1:])

    if not number:
        await update.message.reply_text("❌ Số không hợp lệ!")
        return

    # Lưu số mới vào danh sách
    SCAM_DATABASE[number] = {
        "type": "SĐT / STK Báo cáo",
        "reason": reason
    }

    await update.message.reply_text(f"✅ Đã thêm số `{number}` vào danh sách cảnh báo lừa đảo!", parse_mode="Markdown")

async def check_scam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    clean_input = re.sub(r"\D", "", user_input)

    if not clean_input:
        await update.message.reply_text("❌ Vui lòng nhập đúng định dạng số điện thoại hoặc số tài khoản.")
        return

    if clean_input in SCAM_DATABASE:
        data = SCAM_DATABASE[clean_input]
        bank_info = f" ({data['bank']})" if "bank" in data else ""
        
        reply = (
            f"⚠️ **CẢNH BÁO LỪA ĐẢO!**\n\n"
            f"• **Số kiểm tra:** `{clean_input}`{bank_info}\n"
            f"• **Loại:** {data['type']}\n"
            f"• **Hành vi báo cáo:** {data['reason']}\n\n"
            f"🛑 *Tuyệt đối không thực hiện giao dịch hay cọc tiền cho số này!*"
        )
    else:
        reply = (
            f"✅ **CHƯA PHÁT HIỆN BÁO CÁO**\n\n"
            f"Số `{clean_input}` hiện chưa có trong hệ thống cảnh báo.\n\n"
            f"💡 *Lưu ý: Luôn cảnh giác và xác minh kỹ thông tin trước khi chuyển tiền!*"
        )

    await update.message.reply_text(reply, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report_scam)) # Lệnh thêm số lừa đảo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_scam))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
