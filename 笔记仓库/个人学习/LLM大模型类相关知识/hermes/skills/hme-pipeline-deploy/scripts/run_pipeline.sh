#!/bin/bash
# ============================================================
# HME 流水线触发 + 轮询 + 飞书通知（一体化脚本）
# 一次执行，自动完成全部流程，无需额外权限确认
#
# 用法:
#   bash run_pipeline.sh <pipeline_number> [--no-wait] [--no-notify]
#
# 示例:
#   bash run_pipeline.sh 1              # 触发第1条流水线，轮询等待
#   bash run_pipeline.sh 3 --no-wait    # 仅触发，不等待
#   bash run_pipeline.sh 1 --no-notify  # 不发飞书通知
# ============================================================

set -euo pipefail

# -------------------- 配置 --------------------
PROJECT_ID="3ef9a0702a0b468cb0ae5896a57ccc1e"
BACKEND_POLL=60       # 后端轮询间隔（秒）
FRONTEND_POLL=300      # 前端轮询间隔（秒）
MAX_RETRIES=60        # 最大轮询次数（后端60次=60分钟，前端60次=5小时）

# -------------------- 流水线定义 --------------------
# 格式: 名称|pipeline_id|codehub_id|git_url|分支|imageName|类型(backend/frontend)
PIPELINES=(
  "hmeback-后端-uat打包|fd65ff04186c4e5f9ccaa1cd96ecd29d|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|hme-uat|hmeback|backend"
  "后端-退货uat打包|ead48668623846cd90809a1b1b197ad1|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|hme-uat-return|hmeback|backend"
  "hmefront-前端-uat打包|5ca6e2a5e0ea4ea8a6b0fe622bf321d9|7968367|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmefront.git|uat|hmefront|frontend"
  "前端-退货-uat打包|496b541cae784299a9bb6daa5a249050|7968367|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmefront.git|uat-return|hmefront|frontend"
  "hmeback-后端prod打包|30f86f9940a14bab827ec1a0465100fc|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|hme-prod-release|hmeback|backend"
  "hmefront-前端-prod打包|9f89f799de9b4493af2d27ca54eb3453|7968367|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmefront.git|hme-prod-release|hmefront|frontend"
  "hmeback-后端-DEV打包|bf49dbeca2d84d66977aa871105f6848|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|dev|hmeback|backend"
  "hmefront-前端-DEV打包|f5cc2b8e3fa24b1b891847d4a2ce4ce5|7968367|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmefront.git|dev|hmefront|frontend"
  "hmeback-后端-DEV-退货|cf8fea08e04f481db179568b44665820|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|dev-return|hmeback|backend"
  "hmefront-前端-DEV-退货|d561982c731744d4aef5e68c84d1e247|7968367|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmefront.git|dev-return|hmefront|frontend"
  "hmeback-旧版|e1099de875944f01a208547e73f55778|7968364|https://codehub.devcloud.cn-east-3.huaweicloud.com/3ef9a0702a0b468cb0ae5896a57ccc1e/hmeback.git|dev|hmeback|backend"
)

# -------------------- 颜色 --------------------
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'

log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# -------------------- 飞书通知 --------------------
notify_feishu() {
    local title="$1" content="$2" color="${3:-blue}"
    if [ "$NO_NOTIFY" = true ]; then return; fi
    python ~/.hermes/scripts/feishu_card.py \
        --title "$title" --content "$content" --color "$color" 2>/dev/null || \
    hermes send --to feishu -q "[Pipeline] $title - $content" 2>/dev/null || true
}

# -------------------- 列出流水线 --------------------
list_pipelines() {
    echo ""
    echo -e "${BOLD}可用流水线：${NC}"
    echo ""
    for i in "${!PIPELINES[@]}"; do
        IFS='|' read -r name pid chid gurl branch img ptype <<< "${PIPELINES[$i]}"
        num=$((i + 1))
        interval=$([ "$ptype" = "backend" ] && echo "${BACKEND_POLL}s" || echo "${FRONTEND_POLL}s")
        printf "  ${BOLD}%2d.${NC} %s\n" "$num" "$name"
        echo "      分支: ${branch}  |  类型: ${ptype}  |  轮询: ${interval}"
    done
    echo ""
}

# -------------------- 触发流水线 --------------------
trigger() {
    local pid="$1" chid="$2" gurl="$3" branch="$4" img="$5"

    hcloud CodeArtsPipeline RunPipeline \
        --project_id="$PROJECT_ID" \
        --pipeline_id="$pid" \
        --sources.1.type=code \
        --sources.1.params.git_type=codehub \
        --sources.1.params.codehub_id="$chid" \
        --sources.1.params.git_url="$gurl" \
        --sources.1.params.default_branch="$branch" \
        --sources.1.params.build_params.build_type=branch \
        --sources.1.params.build_params.event_type=Manual \
        --sources.1.params.build_params.target_branch="$branch" \
        --variables.1.name=imageName \
        --variables.1.value="$img" \
        --variables.2.name=orgName \
        --variables.2.value=org \
        --choose_stages.1=state_4 \
        --choose_jobs.1=Task_1 2>&1
}

# -------------------- 查询状态 --------------------
check_status() {
    local pid="$1" run_id="$2"
    hcloud CodeArtsPipeline ShowPipelineRunDetail \
        --project_id="$PROJECT_ID" \
        --pipeline_id="$pid" \
        --pipeline_run_id="$run_id" 2>&1
}

# -------------------- 轮询 --------------------
poll() {
    local pid="$1" run_id="$2" name="$3" branch="$4" ptype="$5" start_time="$6"
    local interval=$([ "$ptype" = "backend" ] && echo "$BACKEND_POLL" || echo "$FRONTEND_POLL")
    local attempt=0

    log_info "开始轮询（间隔: ${interval}s, 最大: ${MAX_RETRIES} 次）..."

    while [ $attempt -lt $MAX_RETRIES ]; do
        attempt=$((attempt + 1))
        sleep "$interval"

        local resp
        resp=$(check_status "$pid" "$run_id")
        local status
        status=$(echo "$resp" | jq -r '.status // "UNKNOWN"' 2>/dev/null || echo "UNKNOWN")

        case "$status" in
            SUCCESS|COMPLETED)
                local end_time=$(date +%s)
                local duration=$(( end_time - start_time ))
                local mins=$(( duration / 60 ))
                local secs=$(( duration % 60 ))
                echo ""
                log_ok "流水线执行成功！(第 ${attempt} 次查询, 耗时: ${mins}分${secs}秒)"
                notify_feishu "✅ 流水线构建成功" \
                    "**流水线**: ${name}\n**分支**: ${branch}\n**运行ID**: ${run_id}\n**耗时**: ${mins}分${secs}秒" \
                    "green"
                return 0
                ;;
            FAILED|FAILURE)
                echo ""
                log_error "流水线执行失败！(第 ${attempt} 次查询)"
                local err_msg
                err_msg=$(echo "$resp" | jq -r '.stages[]? | select(.status=="FAILED") | .name + ": " + .status' 2>/dev/null | head -3)
                notify_feishu "❌ 流水线构建失败" \
                    "**流水线**: ${name}\n**分支**: ${branch}\n**运行ID**: ${run_id}\n**失败阶段**: ${err_msg:-未知}" \
                    "red"
                return 1
                ;;
            CANCELED|CANCELLED)
                echo ""
                log_warn "流水线已取消 (第 ${attempt} 次查询)"
                notify_feishu "⚠️ 流水线已取消" \
                    "**流水线**: ${name}\n**分支**: ${branch}\n**运行ID**: ${run_id}" \
                    "orange"
                return 1
                ;;
            RUNNING|EXECUTING)
                printf "\r${CYAN}[INFO]${NC}  运行中... (第 %d/%d 次查询, %s)    " "$attempt" "$MAX_RETRIES" "$(date '+%H:%M:%S')"
                ;;
            *)
                printf "\r${YELLOW}[WARN]${NC}  状态: %s (第 %d/%d 次查询, %s)    " "$status" "$attempt" "$MAX_RETRIES" "$(date '+%H:%M:%S')"
                ;;
        esac
    done

    echo ""
    log_error "超过最大轮询次数 (${MAX_RETRIES})，停止等待"
    notify_feishu "⏰ 流水线超时" \
        "**流水线**: ${name}\n**分支**: ${branch}\n**运行ID**: ${run_id}\n**已轮询**: ${MAX_RETRIES} 次" \
        "orange"
    return 1
}

# -------------------- 主流程 --------------------
main() {
    local NO_WAIT=false
    local NO_NOTIFY=false
    local PIPELINE_NUM=""

    # 解析参数
    for arg in "$@"; do
        case "$arg" in
            --no-wait)   NO_WAIT=true ;;
            --no-notify) NO_NOTIFY=true ;;
            --list)      list_pipelines; return 0 ;;
            --help|-h)
                echo "用法: bash run_pipeline.sh <序号> [--no-wait] [--no-notify]"
                echo "      bash run_pipeline.sh --list"
                return 0
                ;;
            [0-9]*) PIPELINE_NUM="$arg" ;;
        esac
    done

    echo ""
    echo "=========================================="
    echo "  华为云 CodeArts 流水线自动触发"
    echo "  项目: 欧洲大宗商品交易与风险管理系统"
    echo "=========================================="

    # 未指定序号，列出并提示
    if [ -z "$PIPELINE_NUM" ]; then
        list_pipelines
        read -rp "请输入序号 (1-${#PIPELINES[@]}): " PIPELINE_NUM
    fi

    # 校验序号
    local idx=$((PIPELINE_NUM - 1))
    if [ "$idx" -lt 0 ] || [ "$idx" -ge "${#PIPELINES[@]}" ]; then
        log_error "序号 ${PIPELINE_NUM} 超出范围 (1-${#PIPELINES[@]})"
        return 1
    fi

    # 解析流水线配置
    IFS='|' read -r name pid chid gurl branch img ptype <<< "${PIPELINES[$idx]}"
    local interval=$([ "$ptype" = "backend" ] && echo "${BACKEND_POLL}s" || echo "${FRONTEND_POLL}s")

    log_info "选中: ${name}"
    log_info "分支: ${branch}  |  类型: ${ptype}  |  轮询间隔: ${interval}"
    log_info "Pipeline ID: ${pid}"
    echo ""

    # 触发飞书通知
    notify_feishu "🚀 流水线触发" \
        "**流水线**: ${name}\n**分支**: ${branch}\n**环境**: $([ "$ptype" = "backend" ] && echo "后端" || echo "前端")" \
        "blue"

    # 触发流水线
    log_info "正在触发流水线..."
    local trigger_resp
    trigger_resp=$(trigger "$pid" "$chid" "$gurl" "$branch" "$img")

    local run_id
    run_id=$(echo "$trigger_resp" | jq -r '.pipeline_run_id // empty' 2>/dev/null)

    if [ -z "$run_id" ]; then
        log_error "触发失败！"
        log_error "响应: $(echo "$trigger_resp" | jq -c . 2>/dev/null || echo "$trigger_resp")"
        notify_feishu "❌ 流水线触发失败" \
            "**流水线**: ${name}\n**错误**: $(echo "$trigger_resp" | jq -r '.error_msg // "未知错误"' 2>/dev/null)" \
            "red"
        return 1
    fi

    log_ok "流水线触发成功！"
    log_info "运行实例 ID: ${run_id}"
    echo ""

    # 不等待模式
    if [ "$NO_WAIT" = true ]; then
        log_info "已指定 --no-wait，不等待执行结果"
        return 0
    fi

    # 轮询等待
    local start_time=$(date +%s)
    poll "$pid" "$run_id" "$name" "$branch" "$ptype" "$start_time"
}

main "$@"
